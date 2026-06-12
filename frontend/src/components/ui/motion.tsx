"use client";

import { motion, type HTMLMotionProps } from "motion/react";
import { cn } from "@/lib/utils";

const easeOut = [0.16, 1, 0.3, 1] as const;

/** Apparition en fondu + montée, avec délai paramétrable. */
export function FadeIn({
  children,
  delay = 0,
  y = 16,
  className,
  ...props
}: HTMLMotionProps<"div"> & { delay?: number; y?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay, ease: easeOut }}
      className={cn(className)}
      {...props}
    >
      {children}
    </motion.div>
  );
}

/** Conteneur qui anime ses enfants en cascade (stagger). */
export function Stagger({
  children,
  className,
  delayChildren = 0.05,
  stagger = 0.07,
}: {
  children: React.ReactNode;
  className?: string;
  delayChildren?: number;
  stagger?: number;
}) {
  return (
    <motion.div
      initial="hidden"
      animate="show"
      variants={{
        hidden: {},
        show: { transition: { delayChildren, staggerChildren: stagger } },
      }}
      className={cn(className)}
    >
      {children}
    </motion.div>
  );
}

/** Élément enfant d'un <Stagger>. */
export function StaggerItem({
  children,
  className,
  y = 18,
}: {
  children: React.ReactNode;
  className?: string;
  y?: number;
}) {
  return (
    <motion.div
      variants={{
        hidden: { opacity: 0, y },
        show: { opacity: 1, y: 0, transition: { duration: 0.55, ease: easeOut } },
      }}
      className={cn(className)}
    >
      {children}
    </motion.div>
  );
}
