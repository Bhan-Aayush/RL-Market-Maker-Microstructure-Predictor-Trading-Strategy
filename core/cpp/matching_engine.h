#ifndef MATCHING_ENGINE_H
#define MATCHING_ENGINE_H

#include <string>
#include <vector>
#include <map>
#include <deque>
#include <memory>
#include <optional>

namespace trading {

// Forward declarations
struct Order;
struct Fill;
struct BookSnapshot;

// Order side
enum class Side { BUY, SELL };

// Order type
enum class OrderType { LIMIT, MARKET };

// Order status
enum class OrderStatus { PENDING, ACTIVE, FILLED, PARTIALLY_FILLED, CANCELED };

// Order structure
struct Order {
    std::string order_id;
    std::string client_id;
    Side side;
    OrderType type;
    double price;
    int size;
    int remaining_size;
    double timestamp;
    OrderStatus status;
    
    Order() : price(0.0), size(0), remaining_size(0), timestamp(0.0), 
              status(OrderStatus::PENDING) {}
};

// Fill structure
struct Fill {
    std::string order_id;
    std::string client_id;
    Side side;
    double price;
    int size;
    double timestamp;
    std::string trade_id;
    
    Fill() : price(0.0), size(0), timestamp(0.0) {}
};

// Book snapshot
struct BookSnapshot {
    std::vector<std::pair<double, int>> bids;
    std::vector<std::pair<double, int>> asks;
    std::optional<double> best_bid;
    std::optional<double> best_ask;
    std::optional<double> mid;
    std::optional<double> spread;
    double timestamp;
    
    BookSnapshot() : timestamp(0.0) {}
};

// Limit Order Book
class LimitOrderBook {
public:
    LimitOrderBook(double tick_size = 0.01, int max_levels = 20);
    
    // Order operations
    std::vector<Fill> add_order(const Order& order);
    bool cancel_order(const std::string& order_id);
    std::optional<Order> get_order(const std::string& order_id) const;
    
    // Book queries
    std::optional<double> best_bid() const;
    std::optional<double> best_ask() const;
    std::optional<double> mid_price() const;
    std::optional<double> spread() const;
    BookSnapshot get_book_snapshot(int levels = 10) const;
    
    // Fill history
    std::vector<Fill> get_client_fills(const std::string& client_id) const;
    
private:
    double tick_size_;
    int max_levels_;
    
    // Price-sorted order queues: price -> deque of (order_id, size)
    std::map<double, std::deque<std::pair<std::string, int>>, std::greater<double>> bids_;
    std::map<double, std::deque<std::pair<std::string, int>>> asks_;
    
    // Order registry
    std::map<std::string, Order> orders_;
    
    // Fill history
    std::vector<Fill> fills_;
    
    // Market data cache
    std::optional<double> last_trade_price_;
    int last_trade_size_;
    
    // Helper methods
    double round_price(double price) const;
    std::vector<Fill> match_market_order(Order& order);
    std::vector<Fill> add_limit_order(Order& order);
    void update_last_trade(double price, int size);
};

} // namespace trading

#endif // MATCHING_ENGINE_H
