import { useCallback, useState, type ReactNode } from "react";
import type { Product } from "../../types";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Label } from "@/components/ui/label";
import { TbShirt } from "react-icons/tb";
import { useChat } from "@/store/chat-store";

type ProductDetailsProps = {
  product: Product;
};

const ICONS = {
  clothing: TbShirt,
  shoes: (
    <svg
      fill="#FFF"
      height="16px"
      width="16px"
      version="1.1"
      id="Icons"
      xmlns="http://www.w3.org/2000/svg"
      xmlnsXlink="http://www.w3.org/1999/xlink"
      viewBox="0 0 32 32"
      xmlSpace="preserve"
    >
      <path d="M29,25H3c-0.6,0-1,0.4-1,1s0.4,1,1,1h26c0.6,0,1-0.4,1-1S29.6,25,29,25z" />
      <path
        d="M25.6,15.6l-5.5-0.7C16.6,14.4,14,11.5,14,8c0-0.6-0.4-1-1-1H3C2.4,7,2,7.4,2,8v15c0,0.6,0.4,1,1,1h26c0.6,0,1-0.4,1-1v-2.5
 C30,18,28.1,15.9,25.6,15.6z M8,18c-1.7,0-3-1.3-3-3s1.3-3,3-3s3,1.3,3,3S9.7,18,8,18z M28,22h-7c0-1.6,0.7-3.1,1.9-4.2l0.6-0.5
 l1.9,0.2c1.5,0.2,2.6,1.5,2.6,3V22z"
      />
    </svg>
  ),
  accessories: (
    <svg
      fill="#FFF"
      width="16px"
      height="16px"
      viewBox="0 0 24 24"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path d="M22,9c0,3.19-2.9,5.819-7,6.691V20l-3,2L9,20V15.691C4.9,14.819,2,12.19,2,9S4.984,2.882,9.1,2.021a1,1,0,1,1,.41,1.958C6.367,4.636,4,6.8,4,9c0,2.71,3.664,5,8,5s8-2.29,8-5c0-2.2-2.367-4.364-5.505-5.021a1,1,0,1,1,.41-1.958C19.016,2.882,22,5.817,22,9Z" />
    </svg>
  ),
  bags: (
    <svg
      version="1.0"
      id="Layer_1"
      xmlns="http://www.w3.org/2000/svg"
      width="16px"
      height="16px"
      viewBox="0 0 64 64"
      enableBackground="new 0 0 64 64"
    >
      <polygon
        fill="none"
        stroke="#fff"
        strokeWidth="2"
        strokeMiterlimit="10"
        points="44,18 54,18 54,63 10,63 10,18 20,18 "
      />
      <path
        fill="none"
        stroke="#fff"
        strokeWidth="2"
        strokeMiterlimit="10"
        d="M22,24V11c0-5.523,4.477-10,10-10s10,4.477,10,10v13
 "
      />
    </svg>
  ),
  jewelry: (
    <svg
      width="16px"
      height="16px"
      viewBox="0 0 16 16"
      version="1.1"
      xmlns="http://www.w3.org/2000/svg"
      xmlnsXlink="http://www.w3.org/1999/xlink"
    >
      <path fill="#FFF" d="M0 6h4l3 8.6-7-8.6z"></path>
      <path fill="#FFF" d="M16 6h-4l-3 8.6 7-8.6z"></path>
      <path fill="#FFF" d="M8 15l-3-9h6l-3 9z"></path>
      <path fill="#FFF" d="M4 5h-4l2-3 2 3z"></path>
      <path fill="#FFF" d="M16 5h-4l2-3 2 3z"></path>
      <path fill="#FFF" d="M10 5h-4l2-3 2 3z"></path>
      <path fill="#FFF" d="M3.34 2h3.66l-2 3-1.66-3z"></path>
      <path fill="#FFF" d="M9 2h4l-2 3-2-3z"></path>
    </svg>
  ),
};

const ProductDetails = ({ product }: ProductDetailsProps) => {
  const { sendMessage } = useChat();
  const [selectedSize, setSelectedSize] = useState<string>("");

  const handleSend = useCallback(
    async (message: string) => {
      await sendMessage(message);
    },
    [sendMessage]
  );
  return (
    <Card className="p-5 gap-4">
      <img
        className="w-full object-cover rounded-xl"
        src={product?.images?.full || ""}
        alt={product.name}
      />
      <CardContent className="flex flex-col items-start justify-start p-0">
        <div className="flex flex-col gap-2 items-start justify-start">
          <span className="text-sm ">{product.brand}</span>
          <span className="text-2xl font-medium">{product.name}</span>

          <Badge variant={"secondary"}>
            {ICONS[product.category as keyof typeof ICONS] as ReactNode}{" "}
            {product.category}
          </Badge>
          <p className="text-sm text-muted-foreground">
            ${product.min_price} - ${product.max_price}
          </p>
          <p className="text-xs text-muted-foreground">Unit: {product.unit}</p>
        </div>

        {/* Size Selection */}
        {product.available_sizes && product.available_sizes.length > 0 && (
          <div className="w-full">
            <Label className="text-sm font-medium mb-2 block">
              Available Sizes:
            </Label>
            <RadioGroup
              value={selectedSize}
              onValueChange={setSelectedSize}
              className="flex flex-wrap gap-2"
            >
              {product.available_sizes.map((size) => (
                <div key={size} className="flex items-center space-x-2">
                  <RadioGroupItem value={size} id={`size-${size}`} />
                  <Label
                    htmlFor={`size-${size}`}
                    className="text-xs cursor-pointer px-2 py-1 border rounded hover:bg-gray-50"
                  >
                    {size}
                  </Label>
                </div>
              ))}
            </RadioGroup>
          </div>
        )}
      </CardContent>
      <CardFooter className="flex items-center gap-4 justify-between w-full p-0 mt-2">
        <Button
          className="w-1/2"
          variant={"outline"}
          onClick={() => {
            const sizeText = selectedSize ? ` in size ${selectedSize}` : "";
            const prompt = `Add the ${product.name} by ${product.brand}${sizeText} to my cart.`;
            handleSend(prompt);
          }}
        >
          Add to Cart
        </Button>
        <Button
          className="w-1/2"
          variant={"default"}
          onClick={() => {
            const sizeText = selectedSize ? ` in size ${selectedSize}` : "";
            const prompt = `I'd like to order the ${product.name} by ${product.brand}${sizeText}.`;
            handleSend(prompt);
          }}
        >
          Buy Now
        </Button>
      </CardFooter>
    </Card>
  );
};

export default ProductDetails;
