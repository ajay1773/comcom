import {
  User,
  Mail,
  Phone,
  Calendar,
  ShoppingBag,
  MapPin,
  CheckCircle,
  Clock,
  Edit,
  Eye,
  Settings,
  ShoppingCart,
  Package,
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import type { UserProfileData } from "../../types";
import { get, isEmpty, isNil, size, map } from "lodash";

type Props = {
  data?: UserProfileData;
};

const UserProfile = ({ data }: Props) => {
  if (!data) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <Card>
          <CardContent className="p-8 text-center">
            <User className="size-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Profile Data</h3>
            <p className="text-muted-foreground">
              Unable to load profile information.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const {
    user_details,
    user_orders,
    user_addresses,
    profile_summary,
    suggested_actions,
  } = data;

  // Use lodash for safe property access
  const userFirstName = get(user_details, "first_name", "");
  const userLastName = get(user_details, "last_name", "");
  const userEmail = get(user_details, "email", "");
  const userPhone = get(user_details, "phone", "Not provided");
  const userCreatedAt = get(user_details, "created_at", "");
  const userUpdatedAt = get(user_details, "updated_at", "");
  const accountStatus = get(profile_summary, "account_status", "Unknown");
  const totalOrders = get(profile_summary, "total_orders", 0);
  const totalAddresses = get(profile_summary, "total_addresses", 0);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const getStatusVariant = (status: string) => {
    switch (status.toLowerCase()) {
      case "active":
        return "default";
      case "pending":
        return "secondary";
      case "completed":
        return "default";
      case "shipped":
        return "secondary";
      default:
        return "outline";
    }
  };

  return (
    <div className="max-w-4xl h-full overflow-y-auto">
      {/* Header with success message */}
      <div className="grid grid-cols-3 grid-rows-[repeat(6,fit-content)] gap-5">
        <div className="col-span-3 row-span-1">
          <Card className="h-full w-full">
            <CardContent className="">
              <div className="flex items-start gap-4">
                <div className="rounded-full bg-primary/10 p-3">
                  <User className="size-6 text-primary" />
                </div>
                <div className="flex-1">
                  <h1 className="text-2xl font-bold mb-2">
                    {userFirstName} {userLastName}
                  </h1>
                </div>
                <Badge
                  variant={"default"}
                  className="bg-green-400 text-primary-foreground"
                >
                  <CheckCircle className="size-3 mr-1" />
                  {accountStatus}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="col-span-3 row-span-1">
          <Card className="h-full w-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="size-5" />
                Personal Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center gap-3">
                  <Mail className="size-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">Email</p>
                    <p className="text-sm text-muted-foreground">{userEmail}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Phone className="size-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">Phone</p>
                    <p className="text-sm text-muted-foreground">{userPhone}</p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Calendar className="size-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">Member Since</p>
                    <p className="text-sm text-muted-foreground">
                      {formatDate(userCreatedAt)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Clock className="size-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">Last Updated</p>
                    <p className="text-sm text-muted-foreground">
                      {formatDate(userUpdatedAt)}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="col-span-3 row-span-2">
          <Card className="h-full w-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShoppingBag className="size-5" />
                Order History ({totalOrders})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {!isEmpty(user_orders) ? (
                <Accordion type="single" collapsible className="w-full">
                  {map(user_orders, (order) => {
                    const orderId = get(order, "id", "");
                    const orderNumber = get(order, "order_number", orderId);
                    const orderAmount = get(order, "amount", 0);
                    const paymentStatus = get(order, "payment_status", "");
                    const orderCreatedAt = get(order, "created_at", "");
                    const orderItems = get(order, "items", []);
                    const totalItems = get(
                      order,
                      "total_items",
                      size(orderItems)
                    );

                    return (
                      <AccordionItem
                        key={orderId}
                        value={`order-${orderId}`}
                        className="border-b last:border-b-0"
                      >
                        <AccordionTrigger className="hover:no-underline">
                          <div className="flex items-center justify-between w-full pr-4">
                            <div className="flex items-center gap-3">
                              <div className="flex flex-col items-start">
                                <div className="flex items-center gap-2">
                                  <Package className="size-4 text-muted-foreground" />
                                  <span className="font-medium">
                                    Order #{orderNumber}
                                  </span>
                                </div>
                                <p className="text-sm text-muted-foreground">
                                  {formatDate(orderCreatedAt)}
                                </p>
                              </div>
                              <Badge variant={getStatusVariant(paymentStatus)}>
                                {paymentStatus}
                              </Badge>
                            </div>
                            {/* <div className="flex items-center gap-4 text-sm text-muted-foreground">
                              <span>
                                {totalItems} item{totalItems !== 1 ? "s" : ""}
                              </span>
                              <span className="font-medium text-foreground">
                                ${Number(orderAmount).toFixed(2)}
                              </span>
                              <span>{formatDate(orderCreatedAt)}</span>
                            </div> */}
                          </div>
                        </AccordionTrigger>
                        <AccordionContent>
                          <div className="space-y-3 pt-2">
                            {!isEmpty(orderItems) ? (
                              map(orderItems, (item) => {
                                const itemId = get(item, "id", "");
                                const itemName = get(
                                  item,
                                  "name",
                                  "Unknown Item"
                                );
                                const itemBrand = get(item, "brand", "");
                                const itemSize = get(item, "size", "");
                                const itemColor = get(item, "color", "");
                                const itemQuantity = get(item, "quantity", 1);
                                const itemUnitPrice = get(
                                  item,
                                  "unit_price",
                                  0
                                );
                                const itemTotalPrice = get(
                                  item,
                                  "total_price",
                                  0
                                );
                                const itemStatus = get(item, "status", "");

                                return (
                                  <div
                                    key={itemId}
                                    className="flex items-center justify-between p-3 bg-muted/30 rounded-lg"
                                  >
                                    <div className="flex-1">
                                      <div className="flex items-center gap-2 mb-1">
                                        <h4 className="font-medium text-sm">
                                          {itemName}
                                        </h4>
                                        {!isNil(itemStatus) &&
                                          !isEmpty(itemStatus) && (
                                            <Badge
                                              variant="outline"
                                              className="text-xs"
                                            >
                                              {itemStatus}
                                            </Badge>
                                          )}
                                      </div>
                                      <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                        {!isEmpty(itemBrand) && (
                                          <span>Brand: {itemBrand}</span>
                                        )}
                                        {!isEmpty(itemSize) && (
                                          <span>• Size: {itemSize}</span>
                                        )}
                                        {!isEmpty(itemColor) && (
                                          <span>• Color: {itemColor}</span>
                                        )}
                                        <span>• Qty: {itemQuantity}</span>
                                      </div>
                                    </div>
                                    <div className="text-right">
                                      <div className="font-medium text-sm">
                                        ${Number(itemTotalPrice).toFixed(2)}
                                      </div>
                                      <div className="text-xs text-muted-foreground">
                                        ${Number(itemUnitPrice).toFixed(2)} each
                                      </div>
                                    </div>
                                  </div>
                                );
                              })
                            ) : (
                              <p className="text-sm text-muted-foreground text-center py-4">
                                No items found for this order
                              </p>
                            )}
                          </div>
                        </AccordionContent>
                      </AccordionItem>
                    );
                  })}
                </Accordion>
              ) : (
                <div className="text-center py-8">
                  <ShoppingBag className="size-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No orders yet</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    Start shopping to see your orders here
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="col-span-3 row-span-1">
          <Card className="h-full w-full">
            <CardHeader>
              <CardTitle>Profile Summary</CardTitle>
            </CardHeader>
            <CardContent className="flex justify-between">
              <div className="flex flex-col items-center justify-between gap-2">
                <span className="text-sm text-center">Total Orders</span>
                <Badge variant="secondary">{totalOrders}</Badge>
              </div>
              <div className="flex flex-col items-center justify-between gap-2">
                <span className="text-sm text-center">Saved Addresses</span>
                <Badge variant="secondary">{totalAddresses}</Badge>
              </div>
              <div className="flex flex-col items-center justify-between gap-2">
                <span className="text-sm text-center">Account Status</span>
                <Badge variant={getStatusVariant(accountStatus)}>
                  {accountStatus}
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="col-span-3 row-span-2">
          <Card className="h-full w-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="size-5" />
                Saved Addresses ({totalAddresses})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {!isEmpty(user_addresses) ? (
                <div className="space-y-4">
                  {map(user_addresses, (address) => {
                    const addressId = get(address, "id", "");
                    const addressType = get(address, "type", "");
                    const isDefault = get(address, "is_default", false);
                    const street = get(address, "street", "");
                    const city = get(address, "city", "");
                    const state = get(address, "state", "");
                    const zipCode = get(address, "zip_code", "");
                    const country = get(address, "country", "");

                    return (
                      <div key={addressId} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="capitalize">
                              {addressType}
                            </Badge>
                            {isDefault && (
                              <Badge variant="default">
                                <CheckCircle className="size-3 mr-1" />
                                Default
                              </Badge>
                            )}
                          </div>
                        </div>
                        <p className="text-sm">
                          {street}, {city}, {state} {zipCode}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {country}
                        </p>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="text-center py-8">
                  <MapPin className="size-12 mx-auto text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No addresses saved</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    Add an address to make checkout faster
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        <div className="col-span-3 row-span-1">
          <Card className="h-full w-full">
            <CardHeader>
              <CardTitle className="text-lg font-semibold">
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-4 grid-rows-2">
              {map(suggested_actions, (action, index) => {
                // Define action-specific styling and icons using theme-aware colors
                const getActionConfig = (actionText: string) => {
                  switch (actionText.toLowerCase()) {
                    case "update profile information":
                      return {
                        icon: <Edit className="size-4" />,
                        bgClass:
                          "bg-primary/10 hover:bg-primary/20 border-primary/20 text-primary",
                        iconBg: "bg-primary/20",
                        description: "Edit your personal details",
                      };
                    case "view order history":
                      return {
                        icon: <Eye className="size-4" />,
                        bgClass:
                          "bg-secondary hover:bg-secondary/80 border-border text-secondary-foreground",
                        iconBg: "bg-background",
                        description: "See your past purchases",
                      };
                    case "manage addresses":
                      return {
                        icon: <MapPin className="size-4" />,
                        bgClass:
                          "bg-accent hover:bg-accent/80 border-border text-accent-foreground",
                        iconBg: "bg-background",
                        description: "Update delivery addresses",
                      };
                    case "continue shopping":
                      return {
                        icon: <ShoppingCart className="size-4" />,
                        bgClass:
                          "bg-primary/10 hover:bg-primary/20 border-primary/20 text-primary",
                        iconBg: "bg-primary/20",
                        description: "Browse our products",
                      };
                    default:
                      return {
                        icon: <Settings className="size-4" />,
                        bgClass:
                          "bg-muted hover:bg-muted/80 border-border text-muted-foreground",
                        iconBg: "bg-background",
                        description: "Quick action",
                      };
                  }
                };

                const config = getActionConfig(action);

                return (
                  <div
                    key={index}
                    className={`group relative overflow-hidden rounded-lg border-2 transition-all duration-200 hover:shadow-md hover:scale-[1.02] cursor-pointer ${config.bgClass}`}
                  >
                    <div className="p-4 flex flex-col items-start gap-2">
                      <div className="flex items-center gap-2 w-full">
                        <div
                          className={`p-1.5 rounded-md shadow-sm ${config.iconBg}`}
                        >
                          {config.icon}
                        </div>
                        <div className="flex-1">
                          <h3 className="font-medium text-sm leading-tight">
                            {action}
                          </h3>
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground leading-relaxed">
                        {config.description}
                      </p>

                      {/* Hover effect overlay */}
                      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-transparent to-foreground/5 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />

                      {/* Action indicator */}
                      <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
                        <div className="size-6 rounded-full bg-background/90 border border-border flex items-center justify-center shadow-sm">
                          <div className="size-1.5 rounded-full bg-current" />
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
