import { Button } from "@/components/ui/button";
import type { Product } from "../../types";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { isEmpty } from "lodash";

type ProductsListProps = {
  products: Product[];
  onSelectProduct: (product: Product) => void;
};

const ProductsList = ({ products, onSelectProduct }: ProductsListProps) => {
  return (
    <>
      {!isEmpty(products) && (
        <div className="flex w-full flex-wrap gap-4 h-full overflow-y-auto items-start">
          {products.map((product, index) => (
            <Card
              className=" py-0 gap-4 flex-none w-[calc(50%-0.5rem)]"
              key={index}
            >
              <img
                className="w-full object-cover rounded-t-xl"
                src={product?.images?.full || ""}
                alt={product.name}
              />
              <CardContent className="flex flex-col items-start justify-start px-4">
                <div className="flex flex-col gap-2 items-start justify-start">
                  <span className="text-xs">{product.brand}</span>
                  <span className="text-xl font-medium">{product.name}</span>
                  <p className="text-sm text-muted-foreground">
                    ${product.min_price} per {product.unit}
                  </p>
                  {product.available_sizes &&
                    product.available_sizes.length > 0 && (
                      <p className="text-xs text-muted-foreground">
                        Sizes: {product.available_sizes.join(", ")}
                      </p>
                    )}
                </div>
              </CardContent>
              <CardFooter className="flex items-center flex-col gap-4 justify-between w-full p-4 pt-0">
                <Button
                  className="w-full"
                  variant={"default"}
                  onClick={() => {
                    onSelectProduct(product);
                  }}
                >
                  View Details
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
        // <Carousel className="w-full max-w-xs ml-10">
        //   <CarouselContent>
        //     {products.map((product, index) => (
        //       <CarouselItem key={index}>
        //         <div className="p-1">
        //           <Card className="p-5 gap-4">
        //             <img
        //               className="w-full object-cover rounded-xl"
        //               src={product?.images?.full || ""}
        //               alt={product.name}
        //             />
        //             <CardContent className="flex flex-col items-start justify-start p-0">
        //               <div className="flex flex-col gap-2 items-start justify-start">
        //                 <span className="text-sm ">{product.brand}</span>
        //                 <span className="text-2xl font-medium">
        //                   {product.name}
        //                 </span>

        //                 <Badge variant={"secondary"}>
        //                   <TbShirt /> {product.category}
        //                 </Badge>
        //                 <p className="text-sm text-muted-foreground">
        //                   ${product.min_price} - ${product.max_price}
        //                 </p>
        //               </div>
        //             </CardContent>
        //             <CardFooter className="flex items-center flex-col gap-4 justify-between w-full p-0 mt-2">
        //               <Button
        //                 className="w-full"
        //                 variant={"default"}
        //                 onClick={() => {
        //                   const prompt = `I'd like to order the ${product.name} by ${product.brand}.`;
        //                   handleSend(prompt);
        //                 }}
        //               >
        //                 Buy Now
        //               </Button>
        //               <Button
        //                 className="w-full"
        //                 variant={"outline"}
        //                 onClick={() => {
        //                   const prompt = `Add the ${product.name} by ${product.brand} to my cart.`;
        //                   handleSend(prompt);
        //                 }}
        //               >
        //                 Add to Cart
        //               </Button>
        //             </CardFooter>
        //           </Card>
        //         </div>
        //       </CarouselItem>
        //     ))}
        //   </CarouselContent>
        //   <CarouselPrevious />
        //   <CarouselNext />
        // </Carousel>
      )}
    </>
  );
};

export default ProductsList;
