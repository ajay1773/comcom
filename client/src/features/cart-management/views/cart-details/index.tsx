import { type FC } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { CartDetails as CartDetailsType } from "../../types";
import { get } from "lodash";

type CartDetailsProps = {
  details: CartDetailsType;
};

const CartDetails: FC<CartDetailsProps> = ({ details }) => {
  return (
    <div>
      <Card>
        <CardHeader>
          <CardTitle>Cart Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-2">
            {get(details, "cart_details", []).map((item) => (
              <div key={item.id}>{item.product_id}</div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default CartDetails;
