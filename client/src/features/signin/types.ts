export type SigninSuccess = {
  message: unknown;
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
  };
  jwt_token: string;
};
