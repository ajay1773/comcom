import type { LoginFormData } from "../views/signin-form";

interface SigninResponse {
  success: boolean;
  message: string;
  token?: string;
  user?: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
  };
}

export const signinUser = async (
  credentials: LoginFormData,
  apiBaseUrl: string = "http://localhost:8000"
): Promise<SigninResponse> => {
  const response = await fetch(`${apiBaseUrl}/api/auth/signin`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: credentials.email,
      password: credentials.password,
    }),
  });

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "Sign in failed" }));
    throw new Error(error.detail || "Sign in failed");
  }

  return response.json();
};
