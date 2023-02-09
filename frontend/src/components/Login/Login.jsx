// import "Yoshi-phone.png" from "../../static/images/Yoshi-phone.png";
// Do the above instead of the below
import "./Login.css";
import YoshiPhone from "../../static/images/Yoshi-phone.png";
import { Box, TextField} from "@mui/material"
import { AccountCircle } from '@mui/icons-material';

function Login(props) {
  return (
    <div className="login">
      <div className="login-container">
        <div className="logo">
          <img src={YoshiPhone} alt="Yoshi Phone" />
        </div>
        <div className="login-form">
          <div className="login-form-title">
            <h1>Welcome back!</h1>
          </div>
          <div className="login-form-input">
            <Box sx={{ display: 'flex', flexWrap: 'flex-end' }}>
              <AccountCircle sx={{ color: 'action.active', mr: 1, my: 0.5 }} />
              <TextField id="input-with-sx" label="Username" variant="standard" />
            </Box>
          </div>
        </div>
      </div>
    </div>
  )
}
