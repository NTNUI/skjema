import React, { useState } from 'react';
import { Typography, Button, Paper, CircularProgress } from '@material-ui/core';

import ReceiptIcon from '@material-ui/icons/Receipt';
import Alert from '@material-ui/lab/Alert';

import Input from 'components/Input';
import PictureUpload from 'components/PictureUpload';
import SignatureUpload from 'components/SignatureUpload';
import GroupDropDown from 'components/GroupDropDown';
import LogInAccordion from 'components/LogInAccordion';

import styles from 'components/Form.module.css';
import { updateProfile } from 'service/medlemService';

const Form = (): JSX.Element => {
  const today = new Date().toISOString().split('T')[0].toString();
  const [token, setToken] = useState('');
  
  // Hooks for each field in the form
  const [name, setName] = useState('');
  const [mailfrom, setMailfrom] = useState('');
  const [group, setGroup] = useState('');
  const [mailto, setMailto] = useState('');
  const [accountNumber, setAccountNumber] = useState('');
  const [amount, setAmount] = useState('');
  const [date, setDate] = useState(today);
  const [occasion, setOccasion] = useState('');
  const [comment, setComment] = useState('');
  const [signature, setSignature] = useState('');
  const [images, setImages] = useState<Array<string>>([]);
  

  // Hooks for submittion
  const [submitting, setSumbitting] = useState(false);
  const [success, setSuccess] = useState<boolean | null>(null);
  const [response, setResponse] = useState<string | null>(null);

  // The body object sent to the skjema backend
  const formBody = {
    name,
    mailfrom,
    group,
    mailto,
    accountNumber,
    amount,
    date,
    occasion,
    comment,
    signature,
    images,
  };

  const fillUserInfo = (name: string, mailFrom: string, accountNumber: string, token: string) => {
    setName(name)
    setMailfrom(mailFrom)
    setAccountNumber(accountNumber)
    setToken(token)
  }

  const updateGroup = (group: string) => {
    setGroup(group)
    const groupSlug = group.toLowerCase().replace(' ', '-')
    setMailto(`${groupSlug}-kasserer@ntnui.no`)
  }

  const Response = (): JSX.Element => (
    <div className={styles.response}>
      {/* We have submitted the request, but gotten no response */}
      {submitting && <CircularProgress />}
      {/* We have submitted the request, and gotten succes back */}
      {success == true && <Alert severity="success">{response}</Alert>}
      {/* We have submitted the request, and gotten failure back */}
      {success == false && <Alert severity="error">{response}</Alert>}
    </div>
  );

  return (
    <Paper elevation={3} className={styles.card}>
      <Typography
        variant="h4"
        style={{ width: '100%', textAlign: 'center', marginBottom: '0.5em' }}
      >
        Refusjonsskjema
      </Typography>
      
      <LogInAccordion updateForm={fillUserInfo}/>
      <Input
        name="Navn"
        value={name}
        required
        updateForm={setName}
        helperText="Ditt fulle navn"
      />
      <Input
        name="Din epost"
        value={mailfrom}
        required
        updateForm={setMailfrom}
        helperText="Din kopi av skjema går hit"
      />
      <GroupDropDown updateForm={updateGroup} /> 
      <Input
        name="Din kasserers epost"
        value={mailto}
        required
        updateForm={setMailto}
        helperText="Ofte 'gruppe-kasserer@ntnui.no'"
      />
      <Input
        name="Kontonummer"
        value={accountNumber}
        required
        type="number"
        updateForm={setAccountNumber}
        helperText="Refusjon overføres til denne kontoen"
      />
      <Input
        name="Beløp"
        value={amount}
        required
        type="number"
        updateForm={setAmount}
        adornment={'kr'}
        helperText="Beløpet du ønsker refundert"
      />
      <Input
        name="Kjøpsdato"
        value={date}
        required
        type="date"
        updateForm={setDate}
        helperText="Samme som på kvitteringen"
      />
      <Input
        name="Anledning/arrangement"
        required
        value={occasion}
        updateForm={setOccasion}
        helperText="Som utgiften er knyttet til"
      />
      <Input
        name="Kommentar"
        multiline
        fullWidth
        required
        value={comment}
        updateForm={setComment}
        helperText="Beskriv utgiften"
      />
      <SignatureUpload updateForm={setSignature} setSignature={setSignature} />
      <PictureUpload updateForm={setImages} />
      <Response />
      <Button
        variant="contained"
        color="primary"
        disabled={submitting || success == true}
        style={{ width: '100%', marginTop: '3em' }}
        className={styles.fullWidth}
        onClick={() => {
          updateProfile(token, accountNumber)
          // Reset server response
          setResponse(null);
          setSuccess(null);
          setSumbitting(true);

          // POST full body to the backend
          fetch(`${process.env.API_URL || ''}/kaaf`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify(formBody),
          })
            .then((res) => {
              if (!res.ok) {
                setSuccess(false);
              } else {
                setSuccess(true);
              }
              setSumbitting(false);
              return res.text();
            })
            .then((text) => {
              setResponse(text);
            })
            .catch((err) => {
              setResponse(`Error: ${err.text()}`);
              setSumbitting(false);
            });
        }}
      >
        <ReceiptIcon style={{ marginRight: '10px' }} />
        <Typography variant="h6">Generer bilag</Typography>
      </Button>
    </Paper>
  );
};

export default Form;
