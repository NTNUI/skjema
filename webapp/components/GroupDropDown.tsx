import { useEffect, useState } from 'react';
import Autocomplete from '@material-ui/lab/Autocomplete';
import { Box, FormHelperText, TextField} from '@material-ui/core';
import { fetchGroups } from 'service/medlemService';
import Input from './Input';


type Props = {
    updateForm: (value: string) => void;
  };
const GroupDropDown = ({updateForm}: Props): JSX.Element => {

    const [groups, setGroups] = useState([])
    const getGroups = async () => {
        try {
            const groupResponse = await fetchGroups()
            setGroups(groupResponse)
        }
        finally {

        }
    }
    useEffect(() => {
        getGroups()
    }, [])
    

  return (
      groups.length > 0 ? 
      <Box>
        <Autocomplete
            defaultValue={groups[0]}
            options={groups}
            noOptionsText={"Kunne ikke finne gruppen"}
            getOptionLabel={(option) => option['name']}
            onInputChange={(event, value, reason) => updateForm(value)}
            style={{ width: '250px', marginTop: '1em' }}
            disablePortal={true}
            renderInput={(params) => <TextField {...params} label="Gruppe" variant="outlined"/>}
        />
        <FormHelperText style={{marginLeft: '1em'}}>Som utgiften skal betales av</FormHelperText>
    </Box>
    : 
    <Input
    name="Gruppe"
    required={true}
    updateForm={updateForm}
    helperText="Som utgiften skal betales avhit"
  />
  )
}

export default GroupDropDown;
