"use client";

import React, { useEffect, useState } from "react";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import type { UserAddress } from "../../types";
import { Edit, Plus, ArrowLeft, Trash } from "lucide-react";
import AddressForm from "../address-form";
import { useChat } from "@/store/chat-store";
import { toast } from "sonner";
import { get } from "lodash";

interface UserAddressesWindowProps {
  data: {
    message: { text: string; type: string };
    addresses: UserAddress[];
    suggested_actions: string[];
  };
  onAddressUpdate?: (addresses: UserAddress[]) => void;
}

const UserAddressesWindow: React.FC<UserAddressesWindowProps> = ({
  data = {
    addresses: [],
    suggested_actions: [],
  },
  onAddressUpdate,
}) => {
  const message = get(data, "message.text", "");
  const messageType = get(data, "message.type", "");
  const [showForm, setShowForm] = useState(false);
  const [editingAddress, setEditingAddress] = useState<UserAddress | null>(
    null
  );
  const { sendMessage } = useChat();

  const handleAddNewAddress = () => {
    setEditingAddress(null);
    setShowForm(true);
  };

  const handleEditAddress = (address: UserAddress) => {
    setEditingAddress(address);
    setShowForm(true);
  };

  const handleDeleteAddress = async (address: UserAddress) => {
    const message = `I would like to delete the address with ID ${address.id}`;

    await sendMessage(message);
  };

  const handleBackToList = () => {
    setShowForm(false);
    setEditingAddress(null);
  };

  const handleFormSubmit = async (formData: Omit<UserAddress, "id">) => {
    let updatedAddresses: UserAddress[];

    if (editingAddress) {
      // Update existing address
      updatedAddresses = data.addresses.map((addr) =>
        addr.id === editingAddress.id
          ? { ...formData, id: editingAddress.id }
          : addr
      );
    } else {
      // Add new address
      const newAddress: UserAddress = {
        ...formData,
        id: Date.now(), // Simple ID generation - in real app, this would come from backend
      };
      updatedAddresses = [...data.addresses, newAddress];
    }
    const message = `I would like to ${
      editingAddress ? "update" : "add"
    } the following address ${
      editingAddress ? `with ID ${editingAddress.id}` : ""
    }:
    - Type: ${formData.type}
    - Street: ${formData.street}
    - City: ${formData.city}
    - State: ${formData.state}
    - ZIP Code: ${formData.zip_code}
    - Country: ${formData.country}
    - Is This the Default Address: ${formData.is_default ? "Yes" : "No"}
    `;

    await sendMessage(message);

    onAddressUpdate?.(updatedAddresses);
    handleBackToList();
  };

  useEffect(() => {
    if (messageType === "success") {
      toast.success(message, {
        duration: 3000,
        position: "top-center",
      });
    }
  }, [data, messageType, message]);

  if (showForm) {
    return (
      <Card className="w-full max-w-2xl mx-auto">
        <CardHeader className="relative">
          <Button
            variant="ghost"
            size="icon"
            onClick={handleBackToList}
            className=""
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <CardTitle className="text-center">
            {editingAddress ? "Edit Address" : "Add New Address"}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <AddressForm
            initialData={editingAddress}
            onSubmit={handleFormSubmit}
            onCancel={handleBackToList}
          />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>My Addresses</CardTitle>
      </CardHeader>
      <CardContent>
        {data.addresses.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-muted-foreground mb-4">No addresses right now</p>
            <Button onClick={handleAddNewAddress} className="w-full max-w-xs">
              <Plus className="h-4 w-4 mr-2" />
              Add New Address
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            {data.addresses.map((address) => (
              <div
                key={address.id}
                className="flex items-start justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors"
              >
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="font-medium capitalize">
                      {address.type}
                    </span>
                    {address.is_default && (
                      <Badge variant="secondary" className="text-xs">
                        Default
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {address.street}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {address.city}, {address.state} {address.zip_code}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {address.country}
                  </p>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleEditAddress(address)}
                  className="shrink-0"
                >
                  <Edit className="h-4 w-4" />
                </Button>

                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => handleDeleteAddress(address)}
                  className="shrink-0 hover:text-destructive bg-destructive/10 hover:bg-destructive/20"
                >
                  <Trash className="h-4 w-4 text-destructive" />
                </Button>
              </div>
            ))}
            <Button
              onClick={handleAddNewAddress}
              variant="outline"
              className="w-full"
            >
              <Plus className="h-4 w-4 mr-2" />
              Add New Address
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default UserAddressesWindow;
