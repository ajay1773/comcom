"use client";

import { type FC, useState } from "react";
import { get, isEmpty } from "lodash";
import {
  ChevronDown,
  ChevronUp,
  Package,
  Calendar,
  CreditCard,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

interface OrderItem {
  id: number;
  product_id: number;
  name: string;
  brand: string;
  size?: string;
  color?: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  status: string;
  discount_amount?: number;
}

interface Order {
  id: number;
  order_number: string;
  status: string;
  amount: number;
  currency: string;
  total_items: number;
  payment_status: string;
  payment_method: string;
  shipping_address_id?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
  items: OrderItem[];
}

export interface OrdersWindowProps {
  orders?: Order[];
  loading?: boolean;
  error?: string;
}

const OrdersWindow: FC<OrdersWindowProps> = ({
  orders = [],
  loading = false,
  error,
}) => {
  const [expandedOrders, setExpandedOrders] = useState<Set<number>>(new Set());

  const toggleOrder = (orderId: number) => {
    const newExpanded = new Set(expandedOrders);
    if (newExpanded.has(orderId)) {
      newExpanded.delete(orderId);
    } else {
      newExpanded.add(orderId);
    }
    setExpandedOrders(newExpanded);
  };

  const getStatusVariant = (status: string) => {
    switch (status.toLowerCase()) {
      case "delivered":
        return "default";
      case "confirmed":
      case "processing":
        return "secondary";
      case "shipped":
        return "outline";
      case "cancelled":
        return "destructive";
      default:
        return "outline";
    }
  };

  const getPaymentStatusVariant = (status: string) => {
    switch (status.toLowerCase()) {
      case "paid":
        return "default";
      case "pending":
        return "secondary";
      case "failed":
        return "destructive";
      case "refunded":
        return "outline";
      default:
        return "outline";
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return dateString;
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardHeader>
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </CardHeader>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-red-200">
        <CardContent className="pt-6">
          <div className="text-center text-red-600">
            <Package className="mx-auto h-12 w-12 mb-4 opacity-50" />
            <p className="text-lg font-medium mb-2">Unable to load orders</p>
            <p className="text-sm">{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (isEmpty(orders)) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center text-gray-500">
            <Package className="mx-auto h-12 w-12 mb-4 opacity-50" />
            <p className="text-lg font-medium mb-2">No orders found</p>
            <p className="text-sm">
              Your order history will appear here once you place your first
              order.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4 overflow-y-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">Your Orders</h2>
        <Badge variant="secondary" className="text-sm">
          {orders.length} order{orders.length !== 1 ? "s" : ""}
        </Badge>
      </div>

      {orders.map((order) => {
        const isExpanded = expandedOrders.has(order.id);
        const orderItems = get(order, "items", []);

        return (
          <Card key={order.id} className="overflow-hidden">
            {/* Order Header - Always Visible */}
            <CardHeader
              className="cursor-pointer hover:bg-gray-700/10 transition-colors"
              onClick={() => toggleOrder(order.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <CardTitle className="text-lg flex items-center gap-3">
                    <span>Order #{order.order_number}</span>
                    <Badge variant={getStatusVariant(order.status)}>
                      {order.status}
                    </Badge>
                    <Badge
                      variant={getPaymentStatusVariant(order.payment_status)}
                    >
                      {order.payment_status}
                    </Badge>
                  </CardTitle>

                  <div className="mt-2 grid grid-cols-2 md:grid-cols-2 grid-rows-2 gap-4 text-sm text-gray-600">
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      <span>{formatDate(order.created_at)}</span>
                    </div>

                    <div className="flex items-center gap-2">
                      <Package className="h-4 w-4" />
                      <span>
                        {order.total_items} item
                        {order.total_items !== 1 ? "s" : ""}
                      </span>
                    </div>

                    <div className="flex items-center gap-2">
                      <CreditCard className="h-4 w-4" />
                      <span className="font-medium">
                        {order.currency} {order.amount.toFixed(2)}
                      </span>
                    </div>
                    {order.payment_method && (
                      <div className="mt-2 text-sm text-gray-500">
                        Payment:{" "}
                        {order.payment_method.replace("_", " ").toUpperCase()}
                      </div>
                    )}
                  </div>
                </div>

                <div className="ml-4">
                  {isExpanded ? (
                    <ChevronUp className="h-5 w-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="h-5 w-5 text-gray-400" />
                  )}
                </div>
              </div>
            </CardHeader>

            {/* Order Items - Expandable Content */}
            {isExpanded && (
              <CardContent className="pt-0">
                <Separator className="mb-4" />

                {order.notes && (
                  <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                    <p className="text-sm text-blue-800">
                      <strong>Notes:</strong> {order.notes}
                    </p>
                  </div>
                )}

                <div className="space-y-4">
                  <h4 className="font-medium text-foreground flex items-center gap-2">
                    <Package className="h-4 w-4" />
                    Order Items ({orderItems.length})
                  </h4>

                  {isEmpty(orderItems) ? (
                    <div className="text-center py-8 text-gray-500">
                      <Package className="mx-auto h-8 w-8 mb-2 opacity-50" />
                      <p>No items found for this order</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {orderItems.map((item, index) => (
                        <div
                          key={`${item.id}-${index}`}
                          className="flex items-center justify-between p-4 bg-gray-700/10 rounded-lg border"
                        >
                          <div className="flex-1">
                            <div className="flex items-start justify-between">
                              <div>
                                <h5 className="font-medium text-foreground">
                                  {item.name}
                                  {item.brand && (
                                    <span className="ml-2 text-sm text-gray-500">
                                      by {item.brand}
                                    </span>
                                  )}
                                </h5>

                                <div className="mt-1 flex flex-wrap gap-2 text-sm text-gray-600">
                                  {item.size && (
                                    <span className="bg-white px-2 py-1 rounded border">
                                      Size: {item.size}
                                    </span>
                                  )}
                                  {item.color && (
                                    <span className="bg-white px-2 py-1 rounded border">
                                      Color: {item.color}
                                    </span>
                                  )}
                                  <span className="bg-white px-2 py-1 rounded border">
                                    Qty: {item.quantity}
                                  </span>
                                  {item.status && (
                                    <Badge
                                      variant={getStatusVariant(item.status)}
                                      className="text-xs"
                                    >
                                      {item.status}
                                    </Badge>
                                  )}
                                </div>
                              </div>

                              <div className="text-right ml-4">
                                <div className="font-medium">
                                  ${item.total_price.toFixed(2)}
                                </div>
                                <div className="text-sm text-gray-500">
                                  ${item.unit_price.toFixed(2)} each
                                </div>
                                {item.discount_amount &&
                                  item.discount_amount > 0 && (
                                    <div className="text-sm text-green-600">
                                      -${item.discount_amount.toFixed(2)}{" "}
                                      discount
                                    </div>
                                  )}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                <Separator className="my-4" />

                {/* Order Summary */}
                <div className="bg-gray-700/10 rounded-lg p-4">
                  <div className="flex justify-between items-center text-lg font-semibold">
                    <span>Order Total</span>
                    <span>
                      {order.currency} {order.amount.toFixed(2)}
                    </span>
                  </div>

                  <div className="mt-2 text-sm text-gray-600">
                    <div className="flex justify-between">
                      <span>Items ({order.total_items})</span>
                      <span>
                        {order.currency} {order.amount.toFixed(2)}
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            )}
          </Card>
        );
      })}
    </div>
  );
};

export default OrdersWindow;
