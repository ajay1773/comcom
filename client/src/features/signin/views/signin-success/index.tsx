import StatusCard from "@/components/status-card";
import { CheckCircleIcon } from "lucide-react";
import type { SigninSuccess as SigninSuccessType } from "@/features/signin/types";
import { useEffect } from "react";

const SigninSuccess = ({ details }: { details: SigninSuccessType }) => {
  useEffect(() => {
    localStorage.setItem("jwt_token", details.jwt_token);
  }, [details]);

  return (
    <div>
      <StatusCard
        title="Signin Success"
        subtitle="You have been successfully signed in."
        icon={
          //   <div className="flex w-[100px] h-[100px] rounded-full bg-green-200 opacity-80 items-center justify-center">
          //     <div className="flex w-[80px] h-[80px] rounded-full bg-green-400 opacity-80 items-center justify-center">
          //       <CheckCircleIcon className="w-10 h-10 text-green-600" />
          //     </div>
          //   </div>
          <CheckCircleIcon className="w-10 h-10 text-green-600" />
        }
      />
    </div>
  );
};

export default SigninSuccess;
