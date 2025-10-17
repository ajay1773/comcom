import type { SignupFormData } from "../views/signup-form";

interface SignupResponse {
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

export const signupUser = async (
  data: SignupFormData,
  apiBaseUrl: string = "http://localhost:8000"
): Promise<SignupResponse> => {
  const response = await fetch(`${apiBaseUrl}/api/auth/signup`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email: data.email,
      password: data.password,
      first_name: data.first_name,
      last_name: data.last_name,
      phone: data.phone,
    }),
  });

  if (!response.ok) {
    const error = await response
      .json()
      .catch(() => ({ detail: "Sign up failed" }));
    throw new Error(error.detail || "Sign up failed");
  }

  return response.json();
};
