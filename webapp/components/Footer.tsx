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
    Originalt av og for <strong>Abakus</strong> | Adoptert av <strong>NTNUI</strong> |{' '}
    <a
      style={{
        textDecoration: 'none',
        color: '#BC1818',
      }}
      href="https://github.com/Xtrah/skjema"
      target="blank"
    >
      Bidra her
    </a>
  </div>
);

export default Footer;
