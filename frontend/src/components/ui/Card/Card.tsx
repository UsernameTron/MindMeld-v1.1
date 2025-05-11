import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from "../../../utils/cn";

const cardVariants = cva(
  "rounded-lg border shadow-sm",
  {
    variants: {
      variant: {
        default: "bg-white border-neutral-200",
        ghost: "border-transparent shadow-none",
      },
      category: {
        default: "",
        analyze: "border-analyze-default",
        chat: "border-chat-default",
        rewrite: "border-rewrite-default",
        persona: "border-persona-default",
      },
      size: {
        sm: "p-3",
        md: "p-4",
        lg: "p-6",
      },
      withHover: {
        true: "transition-all duration-200 hover:shadow-md",
        false: "",
      },
    },
    defaultVariants: {
      variant: "default",
      category: "default",
      size: "md",
      withHover: true,
    },
  }
);

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  asChild?: boolean;
  className?: string;
  hasHeaderBorder?: boolean;
  hasFooterBorder?: boolean;
  variant?: 'default' | 'ghost';
  category?: 'default' | 'analyze' | 'chat' | 'rewrite' | 'persona';
  size?: 'sm' | 'md' | 'lg';
  withHover?: boolean;
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ 
    className, 
    variant, 
    category, 
    size, 
    withHover,
    hasHeaderBorder = false,
    hasFooterBorder = false,
    children, 
    ...props 
  }, ref) => {
    return (
      <div
        className={cn(
          cardVariants({ 
            variant, 
            category, 
            size, 
            withHover, 
            className 
          })
        )}
        ref={ref}
        {...props}
      >
        {children}
      </div>
    );
  }
);
Card.displayName = "Card";

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { hasBottomBorder?: boolean }
>(
  ({ className, hasBottomBorder = false, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "flex flex-col space-y-1.5",
          hasBottomBorder && "pb-3 border-b border-neutral-200",
          className
        )}
        {...props}
       />
    );
  }
);
CardHeader.displayName = "CardHeader";

const CardTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement> & { as?: React.ElementType }
>(
  ({ className, as: Component = "h3", ...props }, ref) => {
    return (
      <Component
        ref={ref}
        className={cn("font-semibold leading-none tracking-tight", className)}
        {...props}
       />
    );
  }
);
CardTitle.displayName = "CardTitle";

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(
  ({ className, ...props }, ref) => {
    return (
      <p
        ref={ref}
        className={cn("text-sm text-neutral-500", className)}
        {...props}
       />
    );
  }
);
CardDescription.displayName = "CardDescription";

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("pt-0", className)}
        {...props}
       />
    );
  }
);
CardContent.displayName = "CardContent";

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { hasTopBorder?: boolean }
>(
  ({ className, hasTopBorder = false, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "flex items-center",
          hasTopBorder && "pt-3 mt-3 border-t border-neutral-200",
          className
        )}
        {...props}
       />
    );
  }
);
CardFooter.displayName = "CardFooter";

export { 
  Card, 
  CardHeader, 
  CardFooter, 
  CardTitle, 
  CardDescription, 
  CardContent 
};
