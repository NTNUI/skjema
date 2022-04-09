import React, { useState } from 'react';
import { Typography, Button, Accordion } from '@material-ui/core';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import Alert from '@material-ui/lab/Alert';



import GetAppIcon from '@material-ui/icons/GetApp';


import Input from './Input';

import styles from './Form.module.css';
import { fetchProfile, fetchToken } from 'service/medlemService';


type Props = {
    updateForm: (name: string, mailFrom: string, bankAccount: string, token: string) => void;
  };
const LogInAccordion = ({updateForm}: Props): JSX.Element => {

    const [phoneNumber, setPhoneNumber] = useState('+47');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isSuccess, setIsSuccess] = useState(false);
    const [expanded, setExpanded] = useState(false);


    const fetchUserData = async () => {
        try {
            const token = await fetchToken(phoneNumber, password);
            const profileData = await fetchProfile(token);
            
            const name = `${profileData.first_name} ${profileData.last_name}` ; 
            const mailFrom = profileData.email;
            const accountNumber = profileData.bank_account_number;
            setError('');
            setIsSuccess(true);
            setExpanded(false);
            updateForm(name, mailFrom, accountNumber, token);
        }
        catch (err: any) {
            if (typeof(err) == 'string') {
                setError(err)
            } 
            else setError("Noe gikk galt.")
        }
    }
    
return (
    <Accordion
        defaultExpanded={false}
        disabled={isSuccess}
        expanded={expanded}
        style={{marginBottom: '2em', paddingLeft: '0.5em', paddingRight: '0.5em'}}
        onChange={(e, value) => setExpanded(value)}
        >
        <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            >
            <Typography>Auto-fyll med data fra medlem.ntnui.no (valgfritt)</Typography>
            </AccordionSummary>
        <Input
        name="Telefonnummer"
        value={phoneNumber}
        updateForm={setPhoneNumber}
        helperText="Ditt telefonnummer med landskode" />
        <Input 
        name="Passord"
        value={password}
        updateForm={setPassword}
        helperText="Ditt passord på medlem.ntnui.no"
        type="password"/>
        <Button variant="contained"
            color="primary"
            disabled={isSuccess}
            startIcon={<GetAppIcon/>}
            style={{ width: '100%', marginTop: '1em', marginBottom: '1em' }}
            className={styles.fullWidth}
            onClick={() => fetchUserData()}
        >
            <Typography variant="h6">Hent data fra medlem.ntnui.no</Typography>
        </Button>
        {error && <Alert severity="error">{error}</Alert>}
    </Accordion>
    )
}
export default LogInAccordion;