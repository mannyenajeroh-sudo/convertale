import { Suspense } from "react";
import Header from "@/components/landing/Header";
import Hero from "@/components/landing/Hero";
import ProductFeatures from "@/components/landing/ProductFeatures";
import HowItWorks from "@/components/landing/HowItWorks";
import Proof from "@/components/landing/Proof";
import FinishedOutputProof from "@/components/landing/FinishedOutputProof";
import About from "@/components/landing/About";
import Pricing from "@/components/landing/Pricing";
import CTASection from "@/components/landing/CTASection";
import Footer from "@/components/landing/Footer";

export default function Home() {
  return (
    <>
      <Suspense fallback={null}>
        <Header />
      </Suspense>
      <main>
        <Hero />
        <ProductFeatures />
        <HowItWorks />
        <Proof />
        <FinishedOutputProof />
        <About />
        <Pricing />
        <Suspense fallback={null}>
          <CTASection />
        </Suspense>
      </main>
      <Footer />
    </>
  );
}
