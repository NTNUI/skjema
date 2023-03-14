import React, { useState } from 'react';
import { Typography, Button, Paper, CircularProgress } from '@material-ui/core';
import ReceiptIcon from '@material-ui/icons/Receipt';
import Alert from '@material-ui/lab/Alert';

import Input from './Input';
import SignatureUpload from './SignatureUpload';
import PictureUpload from './PictureUpload';

import styles from './Form.module.css';

const Form = (): JSX.Element => {
  // Get today
  const today = new Date().toISOString().split('T')[0].toString();

  // Hooks for each field in the form
  const [name, setName] = useState('');
  const [mailfrom, setMailfrom] = useState('');
  const [committee, setCommittee] = useState('');
  const [mailto, setMailto] = useState('');
  const [occasion, setOccasion] = useState('');
  const [date, setDate] = useState('');
  const [dateEnd, setDateEnd] = useState('');
  const [destination, setDestination] = useState('');
  const [travelMode, setTravelMode] = useState('');
  const [route, setRoute] = useState('');
  const [distance, setDistance] = useState('');
  const [team, setTeam] = useState('');
  const [numberOfTravelers, setNumberOfTravelers] = useState('');
  const [comment, setComment] = useState('');
  const [accountNumber, setAccountNumber] = useState('');
  const [amount, setAmount] = useState('');
  const [signature, setSignature] = useState('');
  const [images, setImages] = useState<Array<string>>([]);

  // Hooks for submittion
  const [submitting, setSumbitting] = useState(false);
  const [success, setSuccess] = useState<boolean | null>(null);
  const [response, setResponse] = useState<string | null>(null);

  // The body object sendt to the backend
  const formBody = {
    name,
    mailfrom,
    committee,
    mailto,
    occasion,
    date,
    dateEnd,
    destination,
    travelMode,
    route,
    distance,
    team,
    numberOfTravelers,
    comment,
    accountNumber,
    amount,
    signature,
    images,
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
        name="Din e-post"
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
        helperText="Som utgiften skal betales av"
      />
      <Input
        name="Din kasserers e-post"
        value={mailto}
        required
        updateForm={setMailto}
        helperText="Ofte 'gruppe-kasserer@ntnui.no'"
      />
      <Input
        name="Anledning/arrangement"
        required
        fullWidth
        value={occasion}
        updateForm={setOccasion}
        helperText="Som utgiften er knyttet til"
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
        name="Reisemål"
        required
        value={destination}
        updateForm={setDestination}
        helperText="F.eks. 'Domus Athletica, Oslo'"
      />
      <Input
        name="Reisemåte"
        required
        value={travelMode}
        updateForm={setTravelMode}
        helperText="F.eks. leiebil, egen bil, fly"
      />
      <Input
        name="Reiserute"
        required
        value={route}
        updateForm={setRoute}
        helperText="F.eks. 'Trondheim-Oslo-Trondheim'"
      />
      <Input
        name="Antall kilometer"
        required
        value={distance}
        updateForm={setDistance}
        adornment={'km'}
        helperText="Uavhengig av reisemetode"
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
        name="Antall reisende"
        multiline
        required
        value={numberOfTravelers}
        updateForm={setNumberOfTravelers}
        helperText="Hvor mange i reisefølget"
      />
      <Input
        name="Kommentar"
        multiline
        fullWidth
        value={comment}
        updateForm={setComment}
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
        helperText="Totalsum av utlegg"
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
