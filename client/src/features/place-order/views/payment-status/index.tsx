import { Card, CardContent, CardHeader } from "@/components/ui/card";
import type { PaymentStatusDetails } from "../../types";
import { get } from "lodash";
import { LuBadgeCheck, LuBadgeX, LuCheck, LuX } from "react-icons/lu";
import { Badge } from "@/components/ui/badge";
type PaymentStatusProps = {
  details: PaymentStatusDetails;
};

const iconMapForStatus = {
  success: (
    <div className="w-[100px] flex items-center justify-center h-[100px] bg-green-200 rounded-full">
      <LuBadgeCheck className="w-10 h-10 text-green-500" />
    </div>
  ),
  failed: (
    <div className="w-[100px] flex items-center justify-center h-[100px] bg-red-200 rounded-full">
      <LuBadgeX className="w-10 h-10 text-red-500" />
    </div>
  ),
};

const badgeMapForStatus = {
  success: (
    <Badge className="bg-green-200 text-green-500 rounded-full">
      <LuCheck />
      Success
    </Badge>
  ),
  failed: (
    <Badge className="bg-red-200 text-red-500 rounded-full">
      <LuX />
      Failed
    </Badge>
  ),
};

const PaymentStatus = ({ details }: PaymentStatusProps) => {
  const transactionStatus = get(
    details,
    "transaction_details.transaction_status",
    "success"
  );
  return (
    <Card className="w-full">
      <CardHeader className="flex flex-col items-center gap-2">
        {iconMapForStatus[transactionStatus as keyof typeof iconMapForStatus]}
        <h2 className="text-2xl font-bold">
          {transactionStatus === "success"
            ? "Payment Successful"
            : "Payment Failed"}
        </h2>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-2 p-6 rounded-xl border border-neutral-700">
          <h3 className="text-lg font-bold mb-4">Transaction Details</h3>
          <div className="flex justify-between w-full items-center">
            <p className="text-neutral-500 font-medium">Product</p>
            <p>{get(details, "selected_product.name", "")}</p>
          </div>
          <div className="flex justify-between w-full items-center">
            <p className="text-neutral-500 font-medium">Brand</p>
            <p>{get(details, "selected_product.brand", "")}</p>
          </div>
          <div className="flex justify-between w-full items-center">
            <p className="text-neutral-500 font-medium">Transaction Date</p>
            <p>
              {new Date(
                get(details, "transaction_details.transaction_date", "")
              ).toLocaleDateString()}
            </p>
          </div>
          <div className="flex justify-between w-full items-center">
            <p className="text-neutral-500 font-medium">Transaction Type</p>
            <p>{get(details, "transaction_details.transaction_type", "")}</p>
          </div>
          <div className="flex justify-between w-full items-center">
            <p className="text-neutral-500 font-medium">Transaction Status</p>
            <p>
              {
                badgeMapForStatus[
                  transactionStatus as keyof typeof badgeMapForStatus
                ] as React.ReactNode
              }
            </p>
          </div>
          <div className="flex justify-between w-full items-center">
            <p className="text-neutral-500 font-medium">Transaction Amount</p>
            <p>${get(details, "transaction_details.transaction_amount", "")}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default PaymentStatus;
