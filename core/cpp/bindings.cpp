#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include "matching_engine.h"
#include <sstream>

namespace py = pybind11;
using namespace trading;

// Convert Python-friendly types
std::string side_to_string(Side side) {
    return (side == Side::BUY) ? "buy" : "sell";
}

Side string_to_side(const std::string& s) {
    return (s == "buy") ? Side::BUY : Side::SELL;
}

std::string order_type_to_string(OrderType type) {
    return (type == OrderType::LIMIT) ? "limit" : "market";
}

OrderType string_to_order_type(const std::string& s) {
    return (s == "limit") ? OrderType::LIMIT : OrderType::MARKET;
}

// Python-friendly Order class
struct PyOrder {
    std::string order_id;
    std::string client_id;
    std::string side;
    std::string type;
    double price;
    int size;
    int remaining_size;
    double timestamp;
    std::string status;
};

// Python-friendly Fill class
struct PyFill {
    std::string order_id;
    std::string client_id;
    std::string side;
    double price;
    int size;
    double timestamp;
    std::string trade_id;
};

// Convert Order to PyOrder
PyOrder order_to_py(const Order& order) {
    PyOrder py_order;
    py_order.order_id = order.order_id;
    py_order.client_id = order.client_id;
    py_order.side = side_to_string(order.side);
    py_order.type = order_type_to_string(order.type);
    py_order.price = order.price;
    py_order.size = order.size;
    py_order.remaining_size = order.remaining_size;
    py_order.timestamp = order.timestamp;
    
    switch (order.status) {
        case OrderStatus::PENDING: py_order.status = "pending"; break;
        case OrderStatus::ACTIVE: py_order.status = "active"; break;
        case OrderStatus::FILLED: py_order.status = "filled"; break;
        case OrderStatus::PARTIALLY_FILLED: py_order.status = "partially_filled"; break;
        case OrderStatus::CANCELED: py_order.status = "canceled"; break;
    }
    
    return py_order;
}

// Convert PyOrder to Order
Order py_to_order(const PyOrder& py_order) {
    Order order;
    order.order_id = py_order.order_id;
    order.client_id = py_order.client_id;
    order.side = string_to_side(py_order.side);
    order.type = string_to_order_type(py_order.type);
    order.price = py_order.price;
    order.size = py_order.size;
    order.remaining_size = py_order.remaining_size;
    order.timestamp = py_order.timestamp;
    return order;
}

// Convert Fill to PyFill
PyFill fill_to_py(const Fill& fill) {
    PyFill py_fill;
    py_fill.order_id = fill.order_id;
    py_fill.client_id = fill.client_id;
    py_fill.side = side_to_string(fill.side);
    py_fill.price = fill.price;
    py_fill.size = fill.size;
    py_fill.timestamp = fill.timestamp;
    py_fill.trade_id = fill.trade_id;
    return py_fill;
}

PYBIND11_MODULE(matching_engine_core, m) {
    m.doc() = "C++ Matching Engine with Python bindings";
    
    // PyOrder
    py::class_<PyOrder>(m, "Order")
        .def(py::init<>())
        .def_readwrite("order_id", &PyOrder::order_id)
        .def_readwrite("client_id", &PyOrder::client_id)
        .def_readwrite("side", &PyOrder::side)
        .def_readwrite("type", &PyOrder::type)
        .def_readwrite("price", &PyOrder::price)
        .def_readwrite("size", &PyOrder::size)
        .def_readwrite("remaining_size", &PyOrder::remaining_size)
        .def_readwrite("timestamp", &PyOrder::timestamp)
        .def_readwrite("status", &PyOrder::status);
    
    // PyFill
    py::class_<PyFill>(m, "Fill")
        .def(py::init<>())
        .def_readwrite("order_id", &PyFill::order_id)
        .def_readwrite("client_id", &PyFill::client_id)
        .def_readwrite("side", &PyFill::side)
        .def_readwrite("price", &PyFill::price)
        .def_readwrite("size", &PyFill::size)
        .def_readwrite("timestamp", &PyFill::timestamp)
        .def_readwrite("trade_id", &PyFill::trade_id);
    
    // BookSnapshot
    py::class_<BookSnapshot>(m, "BookSnapshot")
        .def(py::init<>())
        .def_readwrite("bids", &BookSnapshot::bids)
        .def_readwrite("asks", &BookSnapshot::asks)
        .def_readwrite("best_bid", &BookSnapshot::best_bid)
        .def_readwrite("best_ask", &BookSnapshot::best_ask)
        .def_readwrite("mid", &BookSnapshot::mid)
        .def_readwrite("spread", &BookSnapshot::spread)
        .def_readwrite("timestamp", &BookSnapshot::timestamp);
    
    // LimitOrderBook
    py::class_<LimitOrderBook>(m, "LimitOrderBook")
        .def(py::init<double, int>(), 
             py::arg("tick_size") = 0.01, 
             py::arg("max_levels") = 20)
        .def("add_order", [](LimitOrderBook& self, const PyOrder& py_order) {
            Order order = py_to_order(py_order);
            std::vector<Fill> fills = self.add_order(order);
            std::vector<PyFill> py_fills;
            for (const auto& fill : fills) {
                py_fills.push_back(fill_to_py(fill));
            }
            return py_fills;
        })
        .def("cancel_order", &LimitOrderBook::cancel_order)
        .def("get_order", [](LimitOrderBook& self, const std::string& order_id) {
            auto order = self.get_order(order_id);
            if (order) {
                return py::cast(order_to_py(*order));
            }
            return py::cast<PyOrder*>(nullptr);
        })
        .def("best_bid", &LimitOrderBook::best_bid)
        .def("best_ask", &LimitOrderBook::best_ask)
        .def("mid_price", &LimitOrderBook::mid_price)
        .def("spread", &LimitOrderBook::spread)
        .def("get_book_snapshot", &LimitOrderBook::get_book_snapshot,
             py::arg("levels") = 10)
        .def("get_client_fills", [](const LimitOrderBook& self, const std::string& client_id) {
            std::vector<Fill> fills = self.get_client_fills(client_id);
            std::vector<PyFill> py_fills;
            for (const auto& fill : fills) {
                py_fills.push_back(fill_to_py(fill));
            }
            return py_fills;
        });
}
