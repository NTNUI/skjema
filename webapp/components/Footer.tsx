import React from 'react';

const Footer = (): JSX.Element => (
  <div
    style={{
      textAlign: 'center',
      width: '100%',
      fontSize: '15px',
      marginTop: '50px',
    }}
  >
    Originalt for <strong>Abakus</strong> | Adoptert av <strong>NTNUI</strong> |{' '}
    <a
      style={{
        textDecoration: 'none',
        color: '#BC1818',
      }}
      href="https://github.com/webkom/kvittering"
      target="blank"
    >
      Bidra her
    </a>
  </div>
);

export default Footer;
