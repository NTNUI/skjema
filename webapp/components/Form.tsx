import React, { useState } from 'react';
import { Typography, Button, Paper, CircularProgress } from '@material-ui/core';
import ReceiptIcon from '@material-ui/icons/Receipt';
import Alert from '@material-ui/lab/Alert';

import Input from './Input';
import PictureUpload from './PictureUpload';
import SignatureUpload from './SignatureUpload';

import styles from './Form.module.css';

const Form = (): JSX.Element => {
  // Get today
  const today = new Date().toISOString().split('T')[0].toString();

  // Hooks for each field in the form
  const [images, setImages] = useState<Array<string>>([]);
  const [date, setDate] = useState('');
  const [occasion, setOccasion] = useState('');
  const [amount, setAmount] = useState('');
  const [comment, setComment] = useState('');
  const [mailto, setMailto] = useState('');
  const [signature, setSignature] = useState('');
  const [name, setName] = useState('');
  const [committee, setCommittee] = useState('');
  const [accountNumber, setAccountNumber] = useState('');
  const [mailfrom, setMailfrom] = useState('');
  const [team, setTeam] = useState('');
  const [dateEnd, setDateEnd] = useState('');
  const [destination, setDestination] = useState('');
  const [route, setRoute] = useState('');
  
  // Hooks for submittion
  const [submitting, setSumbitting] = useState(false);
  const [success, setSuccess] = useState<boolean | null>(null);
  const [response, setResponse] = useState<string | null>(null);

  // The body object sendt to the backend
  const formBody = { 
    images,
    date,
    occasion,
    amount,
    comment,
    mailto,
    signature,
    name,
    committee,
    accountNumber,
    mailfrom,
    team,
    dateEnd,
    destination,
    route
  };

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
        style={{ width: '100%', textAlign: 'center', marginBottom: '1em' }}
      >
        Reiseregningsskjema
      </Typography>
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
      <Input
        name="Gruppe/utvalg"
        value={committee}
        required
        updateForm={setCommittee}
        helperText={'Som utgiften skal betales av'}
      />
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
        name="Reise startdato"
        value={date}
        required
        type="date"
        updateForm={setDate}
        helperText="Dato dere reiste"
      />
      <Input
        name="Reise sluttdato"
        value={dateEnd}
        required
        type="date"
        updateForm={setDateEnd}
        helperText="Dato dere kom hjem"
      />
      <Input
        name="Anledning/arrangement"
        required
        value={occasion}
        updateForm={setOccasion}
        helperText="Som utgiften er knyttet til"
      />
      <Input
        name="Reisefølge"
        multiline
        required
        value={team}
        updateForm={setTeam}
        helperText="Lag og/eller personer som har reist"
      />
      <Input
        name="Reisedestinasjon"
        required
        value={destination}
        updateForm={setDestination}
        helperText="F.eks. 'Domus Athletica, Oslo'"
      />
      <Input
        name="Reiserute"
        multiline
        required
        value={route}
        updateForm={setRoute}
        helperText="F.eks. 'Trondheim-Oslo-Trondheim'"
      />
      <Input
        name="Kommentar"
        multiline
        fullWidth
        value={comment}
        updateForm={setComment}
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
        <Typography variant="h6">Send reiseregning</Typography>
      </Button>
    </Paper>
  );
};

export default Form;
