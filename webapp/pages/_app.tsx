import React from 'react';
import './_app.css';
import Head from 'next/head';

// eslint-disable-next-line
export default function MyApp({ Component, pageProps }: any): JSX.Element {
  return (
    <>
      <Head>
        <title>Refusjonsskjema for NTNUI</title>
      </Head>
      <Component {...pageProps} />
    </>
  )
}
