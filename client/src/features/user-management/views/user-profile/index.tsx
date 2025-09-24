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
} from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { UserProfileData } from "../../types";

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
                    {user_details.first_name} {user_details.last_name}
                  </h1>
                </div>
                <Badge
                  variant={"default"}
                  className="bg-green-400 text-primary-foreground"
                >
                  <CheckCircle className="size-3 mr-1" />
                  {profile_summary.account_status}
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
                    <p className="text-sm text-muted-foreground">
                      {user_details.email}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Phone className="size-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">Phone</p>
                    <p className="text-sm text-muted-foreground">
                      {user_details.phone}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Calendar className="size-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">Member Since</p>
                    <p className="text-sm text-muted-foreground">
                      {formatDate(user_details.created_at)}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3">
                  <Clock className="size-4 text-muted-foreground" />
                  <div>
                    <p className="text-sm font-medium">Last Updated</p>
                    <p className="text-sm text-muted-foreground">
                      {formatDate(user_details.updated_at)}
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="col-span-2 row-span-2">
          <Card className="h-full w-full">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShoppingBag className="size-5" />
                Order History ({profile_summary.total_orders})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {user_orders.length > 0 ? (
                <div className="space-y-4">
                  {user_orders.map((order) => (
                    <div key={order.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">Order #{order.id}</span>
                          <Badge variant={getStatusVariant(order.status)}>
                            {order.status}
                          </Badge>
                        </div>
                        <span className="text-sm text-muted-foreground">
                          {formatDate(order.created_at)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium">
                            {order.product_name}
                          </p>
                          <p className="text-sm text-muted-foreground">
                            Qty: {order.quantity} • {order.brand} •{" "}
                            {order.category}
                          </p>
                        </div>
                        <span className="font-medium">
                          ${order.price.toFixed(2)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
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

        <div className="col-span-1 row-span-2">
          <Card className="h-full w-full">
            <CardHeader>
              <CardTitle>Profile Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex flex-col items-center justify-between gap-2">
                <span className="text-sm text-center">Total Orders</span>
                <Badge variant="secondary">
                  {profile_summary.total_orders}
                </Badge>
              </div>
              <div className="flex flex-col items-center justify-between gap-2">
                <span className="text-sm text-center">Saved Addresses</span>
                <Badge variant="secondary">
                  {profile_summary.total_addresses}
                </Badge>
              </div>
              <div className="flex flex-col items-center justify-between gap-2">
                <span className="text-sm text-center">Account Status</span>
                <Badge
                  variant={getStatusVariant(profile_summary.account_status)}
                >
                  {profile_summary.account_status}
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
                Saved Addresses ({profile_summary.total_addresses})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {user_addresses.length > 0 ? (
                <div className="space-y-4">
                  {user_addresses.map((address) => (
                    <div key={address.id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="capitalize">
                            {address.type}
                          </Badge>
                          {address.is_default && (
                            <Badge variant="default">
                              <CheckCircle className="size-3 mr-1" />
                              Default
                            </Badge>
                          )}
                        </div>
                      </div>
                      <p className="text-sm">
                        {address.street}, {address.city}, {address.state}{" "}
                        {address.zip_code}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {address.country}
                      </p>
                    </div>
                  ))}
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
              {suggested_actions.map((action, index) => {
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
