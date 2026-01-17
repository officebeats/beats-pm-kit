import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { motion, AnimatePresence } from "motion/react";
import { cn } from "@/lib/utils";

// -----------------------------------------------------------------------------
// 1. Definition & Tokens
// -----------------------------------------------------------------------------
const componentVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive:
          "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline:
          "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary:
          "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "size-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

// -----------------------------------------------------------------------------
// 2. Interface
// -----------------------------------------------------------------------------
export interface ComponentProps
  extends
    React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof componentVariants> {
  asChild?: boolean;
}

// -----------------------------------------------------------------------------
// 3. Implementation
// -----------------------------------------------------------------------------
const Component = React.forwardRef<HTMLButtonElement, ComponentProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    // Note: If asChild is true, we would use a Slot component (requires @radix-ui/react-slot)
    // For this template, we assume standard element usage.

    return (
      <motion.button
        whileTap={{ scale: 0.95 }}
        className={cn(componentVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  },
);
Component.displayName = "Component";

export { Component, componentVariants };
