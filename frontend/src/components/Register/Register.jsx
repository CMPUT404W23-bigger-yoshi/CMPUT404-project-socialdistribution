import "./Register.css";
import Logo from "../Logo/Logo";
import {Button, Col, Form, InputGroup, Row} from "react-bootstrap";
import {EnvelopeFill, KeyFill} from "react-bootstrap-icons";
import {useState} from "react";
import {register} from "../../services/auth";

function Register(props) {

  const [formData, setFormData] = useState({
    username: "",
    password: "",
    confirmPassword: "",
  });

  const handleSubmit = (e) => {
    // Perform validation here
    e.preventDefault();
    console.log(formData);
    register(formData)
      .then((response) => {
        console.log(response);
      })
      .catch((error) => {
        console.log(error);
      });
  }

  return (
    <div className="register">
      <div className="register-container">
        <Row style={{height: "20vh"}}>
          <Logo size={"100px"}/>
        </Row>
        <Row style={{height: "10vh"}}>
          <div className="register-form-title">
            <h1>Create Account</h1>
          </div>
        </Row>
        <Row style={{height: "50vh"}}>
          <div className="register-form-input">
            <Form>
              <Form.Group
                controlId="formBasicUsername"
                className="formBasicUsername"
                as={Col}>
                <Form.Label>Username</Form.Label>
                <InputGroup>
                  <InputGroup.Text>
                    <EnvelopeFill/>
                  </InputGroup.Text>
                  <Form.Control
                    type="text"
                    placeholder="Enter username"
                    onChange={(e) => {
                      setFormData({...formData, username: e.target.value});
                    }}
                  />
                </InputGroup>
              </Form.Group>

              <Form.Group
                controlId="formBasicPassword"
                className="formBasicPassword"
                as={Col}>
                <Form.Label>Password</Form.Label>
                <InputGroup>
                  <InputGroup.Text>
                    <KeyFill/>
                  </InputGroup.Text>
                  <Form.Control
                    type="password"
                    placeholder="Password"
                    onChange={(e) => {
                      setFormData({...formData, password: e.target.value});
                    }}
                  />
                </InputGroup>
              </Form.Group>

              <Form.Group
                controlId="formBasicPassword"
                className="formBasicPassword"
                as={Col}>
                <Form.Label>Confirm Password</Form.Label>
                <InputGroup>
                  <InputGroup.Text>
                    <KeyFill/>
                  </InputGroup.Text>
                  <Form.Control
                    type="password"
                    placeholder="Password"
                    onChange={(e) => {
                      setFormData({...formData, confirmPassword: e.target.value});
                    }}
                  />
                </InputGroup>
              </Form.Group>


              <Button
                variant="primary"
                type="submit"
                onClick={handleSubmit}
              >
                Sign Up!
              </Button>
            </Form>
          </div>
        </Row>

        <Row style={{height: "15vh"}}>
          <div className="register-form-signup">
            <Row xs={2}>
              <Col
                className="signup-text"
                xs={8}>
                <p>Already have an account?</p>
              </Col>
              <Col
                className="signup-link"
                xs={4}
                onClick={() => {
                  window.location.href = "/login"
                }}>
                <p
                >Login here</p>
              </Col>
            </Row>
          </div>
        </Row>
      </div>
    </div>
  )
}

export default Register;
