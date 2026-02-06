#include "matching_engine.h"
#include <algorithm>
#include <cmath>
#include <ctime>
#include <random>
#include <sstream>
#include <iomanip>
#include <chrono>

namespace trading {

LimitOrderBook::LimitOrderBook(double tick_size, int max_levels)
    : tick_size_(tick_size), max_levels_(max_levels), last_trade_size_(0) {}

double LimitOrderBook::round_price(double price) const {
    return std::round(price / tick_size_) * tick_size_;
}

std::optional<double> LimitOrderBook::best_bid() const {
    if (bids_.empty()) return std::nullopt;
    return bids_.begin()->first;
}

std::optional<double> LimitOrderBook::best_ask() const {
    if (asks_.empty()) return std::nullopt;
    return asks_.begin()->first;
}

std::optional<double> LimitOrderBook::mid_price() const {
    auto bb = best_bid();
    auto ba = best_ask();
    if (bb && ba) {
        return (*bb + *ba) / 2.0;
    }
    return last_trade_price_;
}

std::optional<double> LimitOrderBook::spread() const {
    auto bb = best_bid();
    auto ba = best_ask();
    if (bb && ba) {
        return *ba - *bb;
    }
    return std::nullopt;
}

void LimitOrderBook::update_last_trade(double price, int size) {
    last_trade_price_ = price;
    last_trade_size_ = size;
}

std::vector<Fill> LimitOrderBook::match_market_order(Order& order) {
    std::vector<Fill> fills;
    
    auto& opposite_book = (order.side == Side::BUY) ? asks_ : bids_;
    
    if (opposite_book.empty()) {
        order.status = OrderStatus::PENDING;
        return fills;
    }
    
    // For buys: consume asks (lowest first)
    // For sells: consume bids (highest first)
    auto it = opposite_book.begin();
    
    while (it != opposite_book.end() && order.remaining_size > 0) {
        double price = it->first;
        auto& queue = it->second;
        
        while (!queue.empty() && order.remaining_size > 0) {
            auto& [other_order_id, available_size] = queue.front();
            
            if (orders_.find(other_order_id) == orders_.end()) {
                queue.pop_front();
                continue;
            }
            
            Order& other_order = orders_[other_order_id];
            int fill_size = std::min(order.remaining_size, other_order.remaining_size);
            
            // Generate trade ID
            static std::random_device rd;
            static std::mt19937 gen(rd());
            static std::uniform_int_distribution<> dis(1000000, 9999999);
            std::string trade_id = "T" + std::to_string(dis(gen));
            
            // Create fills
            Fill fill1;
            fill1.order_id = order.order_id;
            fill1.client_id = order.client_id;
            fill1.side = order.side;
            fill1.price = price;
            fill1.size = fill_size;
            auto now = std::chrono::system_clock::now();
            auto timestamp = std::chrono::duration_cast<std::chrono::seconds>(
                now.time_since_epoch()).count();
            fill1.timestamp = static_cast<double>(timestamp);
            fill1.trade_id = trade_id;
            
            Fill fill2;
            fill2.order_id = other_order_id;
            fill2.client_id = other_order.client_id;
            fill2.side = other_order.side;
            fill2.price = price;
            fill2.size = fill_size;
            fill2.timestamp = fill1.timestamp;
            fill2.trade_id = trade_id;
            
            fills.push_back(fill1);
            fills_.push_back(fill1);
            fills_.push_back(fill2);
            
            // Update sizes
            order.remaining_size -= fill_size;
            other_order.remaining_size -= fill_size;
            
            // Update other order status
            if (other_order.remaining_size == 0) {
                other_order.status = OrderStatus::FILLED;
                queue.pop_front();
            } else {
                other_order.status = OrderStatus::PARTIALLY_FILLED;
                queue.front().second = other_order.remaining_size;
            }
            
            update_last_trade(price, fill_size);
        }
        
        // Remove empty price levels
        if (queue.empty()) {
            it = opposite_book.erase(it);
        } else {
            ++it;
        }
    }
    
    // Update order status
    if (order.remaining_size == 0) {
        order.status = OrderStatus::FILLED;
    } else if (order.remaining_size < order.size) {
        order.status = OrderStatus::PARTIALLY_FILLED;
    }
    
    return fills;
}

std::vector<Fill> LimitOrderBook::add_limit_order(Order& order) {
    std::vector<Fill> fills;
    
    double price = round_price(order.price);
    order.price = price;
    
    // Try to match against opposite side
    auto& opposite_book = (order.side == Side::BUY) ? asks_ : bids_;
    
    if (!opposite_book.empty()) {
        if (order.side == Side::BUY) {
            // Buy order: match if price >= best ask
            auto best_opposite = asks_.begin()->first;
            if (price >= best_opposite) {
                fills = match_market_order(order);
            }
        } else {
            // Sell order: match if price <= best bid
            auto best_opposite = bids_.begin()->first;
            if (price <= best_opposite) {
                fills = match_market_order(order);
            }
        }
    }
    
    // If still has remaining size, add to book
    if (order.remaining_size > 0) {
        auto& book = (order.side == Side::BUY) ? bids_ : asks_;
        book[price].push_back({order.order_id, order.remaining_size});
        if (order.status == OrderStatus::PENDING) {
            order.status = OrderStatus::ACTIVE;
        }
    }
    
    return fills;
}

std::vector<Fill> LimitOrderBook::add_order(const Order& order_in) {
    Order order = order_in;
    order.remaining_size = order.size;
    orders_[order.order_id] = order;
    
    if (order.type == OrderType::MARKET) {
        return match_market_order(orders_[order.order_id]);
    } else {
        return add_limit_order(orders_[order.order_id]);
    }
}

bool LimitOrderBook::cancel_order(const std::string& order_id) {
    auto it = orders_.find(order_id);
    if (it == orders_.end()) {
        return false;
    }
    
    Order& order = it->second;
    if (order.status == OrderStatus::FILLED || order.status == OrderStatus::CANCELED) {
        return false;
    }
    
    // Remove from book
    auto& book = (order.side == Side::BUY) ? bids_ : asks_;
    double price = order.price;
    
    auto price_it = book.find(price);
    if (price_it != book.end()) {
        auto& queue = price_it->second;
        queue.erase(
            std::remove_if(queue.begin(), queue.end(),
                [&order_id](const auto& item) { return item.first == order_id; }),
            queue.end()
        );
        
        if (queue.empty()) {
            book.erase(price_it);
        }
    }
    
    order.status = OrderStatus::CANCELED;
    return true;
}

std::optional<Order> LimitOrderBook::get_order(const std::string& order_id) const {
    auto it = orders_.find(order_id);
    if (it == orders_.end()) {
        return std::nullopt;
    }
    return it->second;
}

BookSnapshot LimitOrderBook::get_book_snapshot(int levels) const {
    BookSnapshot snapshot;
    auto now = std::chrono::system_clock::now();
    auto timestamp = std::chrono::duration_cast<std::chrono::seconds>(
        now.time_since_epoch()).count();
    snapshot.timestamp = static_cast<double>(timestamp);
    snapshot.best_bid = best_bid();
    snapshot.best_ask = best_ask();
    snapshot.mid = mid_price();
    snapshot.spread = spread();
    
    // Get top N bid levels
    int bid_count = 0;
    for (const auto& [price, queue] : bids_) {
        if (bid_count >= levels) break;
        int total_size = 0;
        for (const auto& [_, size] : queue) {
            total_size += size;
        }
        snapshot.bids.push_back({price, total_size});
        bid_count++;
    }
    
    // Get top N ask levels
    int ask_count = 0;
    for (const auto& [price, queue] : asks_) {
        if (ask_count >= levels) break;
        int total_size = 0;
        for (const auto& [_, size] : queue) {
            total_size += size;
        }
        snapshot.asks.push_back({price, total_size});
        ask_count++;
    }
    
    return snapshot;
}

std::vector<Fill> LimitOrderBook::get_client_fills(const std::string& client_id) const {
    std::vector<Fill> client_fills;
    for (const auto& fill : fills_) {
        if (fill.client_id == client_id) {
            client_fills.push_back(fill);
        }
    }
    return client_fills;
}

} // namespace trading
