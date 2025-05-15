import React, { useState } from 'react';
import type { NextPage } from 'next';
import Head from 'next/head';
import Link from 'next/link';

const Home: NextPage = () => {
  const [email, setEmail] = useState('');

  const features = [
    {
      title: 'AI-Powered Lead Scoring',
      description: 'Our ML models analyze leads to find the best prospects for your business.',
      icon: '🎯'
    },
    {
      title: 'Email Prediction',
      description: 'Automatically predict email formats based on names and company domains.',
      icon: '📧'
    },
    {
      title: 'Lead Discovery',
      description: 'Find high-quality leads from LinkedIn and company websites.',
      icon: '🔍'
    },
    {
      title: 'AI Email Generation',
      description: 'Create personalized email campaigns with cutting-edge GPT technology.',
      icon: '✍️'
    }
  ];
  
  const testimonials = [
    {
      quote: "This tool has revolutionized our outreach strategy. We've seen a 300% increase in response rates.",
      author: "Sarah Johnson",
      company: "Growth Marketing, TechCorp",
      image: "/avatars/avatar1.svg"
    },
    {
      quote: "The lead scoring is incredibly accurate. We're now focusing on leads that actually convert.",
      author: "Michael Chen",
      company: "Sales Director, Innovate Inc",
      image: "/avatars/avatar2.svg"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50">
      <Head>
        <title>LeadAI - AI-Powered Lead Generation</title>
        <meta name="description" content="Generate, score, and engage with high-quality leads using AI" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0 flex items-center">
                <span className="text-2xl font-bold text-primary-600">LeadAI</span>
              </div>
            </div>
            <div className="flex items-center">
              <Link href="/login" className="px-4 py-2 text-sm text-gray-700 hover:text-gray-900">
                Log in
              </Link>
              <Link href="/signup" className="ml-4 px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-md">
                Sign up
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="pt-16 pb-20 sm:pt-24 sm:pb-32 lg:pt-32 lg:pb-36">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="lg:grid lg:grid-cols-12 lg:gap-8">
            <div className="sm:text-center md:max-w-2xl md:mx-auto lg:col-span-6 lg:text-left">
              <h1 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl md:text-6xl">
                <span className="block">Find and engage with</span>
                <span className="block text-primary-600">high-quality leads</span>
                <span className="block">powered by AI</span>
              </h1>
              <p className="mt-3 text-base text-gray-500 sm:mt-5 sm:text-xl lg:text-lg xl:text-xl">
                Our AI-powered lead generation tool helps you discover, score, and engage with the right prospects, 
                saving you time and increasing your conversion rates.
              </p>
              <div className="mt-8 sm:max-w-lg sm:mx-auto sm:text-center lg:text-left lg:mx-0">
                <form className="mt-3 sm:flex">
                  <label htmlFor="email" className="sr-only">Email</label>
                  <input
                    type="email"
                    name="email"
                    id="email"
                    className="block w-full py-3 px-4 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 border-gray-300"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                  <button
                    type="submit"
                    className="mt-3 w-full px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-primary-600 shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:mt-0 sm:ml-3 sm:flex-shrink-0 sm:inline-flex sm:items-center sm:w-auto"
                  >
                    Get Started
                  </button>
                </form>
                <p className="mt-3 text-sm text-gray-500">
                  Start free. No credit card required.
                </p>
              </div>
            </div>
            <div className="mt-12 relative sm:max-w-lg sm:mx-auto lg:mt-0 lg:max-w-none lg:mx-0 lg:col-span-6 lg:flex lg:items-center">
              <div className="relative mx-auto w-full rounded-lg shadow-lg lg:max-w-md">
                <div className="relative block w-full bg-white rounded-lg overflow-hidden">
                  <span className="sr-only">Watch our video</span>
                  <img
                    className="w-full"
                    src="https://via.placeholder.com/1200x700/5271FF/FFFFFF?text=AI+Lead+Generation+Demo"
                    alt="Demo screenshot"
                  />
                  <div className="absolute inset-0 w-full h-full flex items-center justify-center">
                    <svg 
                      className="h-20 w-20 text-primary-500"
                      fill="currentColor"
                      viewBox="0 0 84 84">
                      <circle opacity="0.9" cx="42" cy="42" r="42" fill="white" />
                      <path d="M55 41.5L36 55V28L55 41.5Z" fill="#5271FF" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Feature Section */}
      <div className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-base font-semibold text-primary-600 tracking-wide uppercase">Features</h2>
            <p className="mt-1 text-4xl font-extrabold text-gray-900 sm:text-5xl sm:tracking-tight lg:text-6xl">
              Everything you need to succeed
            </p>
            <p className="max-w-xl mt-5 mx-auto text-xl text-gray-500">
              Our comprehensive lead generation platform combines AI, machine learning, and automation to supercharge your sales.
            </p>
          </div>

          <div className="mt-12">
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-4">
              {features.map((feature) => (
                <div key={feature.title} className="pt-6">
                  <div className="flow-root bg-gray-50 rounded-lg px-6 pb-8">
                    <div className="-mt-6">
                      <div>
                        <span className="inline-flex items-center justify-center p-3 bg-primary-500 rounded-md shadow-lg text-3xl">
                          {feature.icon}
                        </span>
                      </div>
                      <h3 className="mt-8 text-lg font-medium text-gray-900 tracking-tight">{feature.title}</h3>
                      <p className="mt-5 text-base text-gray-500">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Testimonials */}
      <div className="bg-gray-50 py-16 sm:py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-base font-semibold text-primary-600 tracking-wide uppercase">Testimonials</h2>
            <p className="mt-2 text-3xl font-extrabold text-gray-900 tracking-tight sm:text-4xl">
              Trusted by businesses worldwide
            </p>
          </div>
          <div className="mt-12">
            <div className="grid grid-cols-1 gap-y-12 gap-x-6 md:grid-cols-2">
              {testimonials.map((testimonial) => (
                <div key={testimonial.author} className="bg-white p-8 border border-gray-200 rounded-lg shadow-sm">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <img className="h-12 w-12 rounded-full" src={testimonial.image} alt={testimonial.author} />
                    </div>
                    <div className="ml-4">
                      <h4 className="text-lg font-bold text-gray-900">{testimonial.author}</h4>
                      <p className="text-gray-500">{testimonial.company}</p>
                    </div>
                  </div>
                  <p className="mt-4 text-lg text-gray-600 italic">"{testimonial.quote}"</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-primary-700">
        <div className="max-w-2xl mx-auto text-center py-16 px-4 sm:py-20 sm:px-6 lg:px-8">
          <h2 className="text-3xl font-extrabold text-white sm:text-4xl">
            <span className="block">Ready to boost your lead generation?</span>
            <span className="block">Start using LeadAI today.</span>
          </h2>
          <p className="mt-4 text-lg leading-6 text-primary-200">
            Sign up now and get 50 free lead credits. No credit card required.
          </p>
          <Link href="/signup" className="mt-8 w-full inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-primary-600 bg-white hover:bg-primary-50 sm:w-auto">
            Get started
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white">
        <div className="max-w-7xl mx-auto py-12 px-4 overflow-hidden sm:px-6 lg:px-8">
          <nav className="-mx-5 -my-2 flex flex-wrap justify-center" aria-label="Footer">
            <div className="px-5 py-2">
              <Link href="/about" className="text-base text-gray-500 hover:text-gray-900">
                About
              </Link>
            </div>
            <div className="px-5 py-2">
              <Link href="/features" className="text-base text-gray-500 hover:text-gray-900">
                Features
              </Link>
            </div>
            <div className="px-5 py-2">
              <Link href="/pricing" className="text-base text-gray-500 hover:text-gray-900">
                Pricing
              </Link>
            </div>
            <div className="px-5 py-2">
              <Link href="/blog" className="text-base text-gray-500 hover:text-gray-900">
                Blog
              </Link>
            </div>
            <div className="px-5 py-2">
              <Link href="/contact" className="text-base text-gray-500 hover:text-gray-900">
                Contact
              </Link>
            </div>
          </nav>
          <p className="mt-8 text-center text-base text-gray-400">
            &copy; {new Date().getFullYear()} LeadAI. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Home;
