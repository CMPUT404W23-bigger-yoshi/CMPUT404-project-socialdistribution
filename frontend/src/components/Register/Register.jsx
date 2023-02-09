import "./Register.css";
import Logo from "../Logo/Logo";
import {Button, Col, Form, InputGroup, Row} from "react-bootstrap";
import {EnvelopeFill, KeyFill} from "react-bootstrap-icons";

function Register(props) {
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
              <Form.Group controlId="formBasicEmail" className="formBasicEmail" as={Col}>
                <Form.Label>Email</Form.Label>
                <InputGroup>
                  <InputGroup.Text>
                    <EnvelopeFill/>
                  </InputGroup.Text>
                  <Form.Control type="email" placeholder="Enter email"/>
                </InputGroup>
              </Form.Group>

              <Form.Group controlId="formBasicPassword" className="formBasicPassword" as={Col}>
                <Form.Label>Password</Form.Label>
                <InputGroup>
                  <InputGroup.Text>
                    <KeyFill/>
                  </InputGroup.Text>
                  <Form.Control type="password" placeholder="Password"/>
                </InputGroup>
              </Form.Group>

              <Form.Group controlId="formBasicPassword" className="formBasicPassword" as={Col}>
                <Form.Label>Confirm Password</Form.Label>
                <InputGroup>
                  <InputGroup.Text>
                    <KeyFill/>
                  </InputGroup.Text>
                  <Form.Control type="password" placeholder="Password"/>
                </InputGroup>
              </Form.Group>


              <Button variant="primary" type="submit">
                Sign Up!
              </Button>
            </Form>
          </div>
        </Row>

        <Row style={{height: "15vh"}}>
          <div className="register-form-signup">
            <Row xs={2}>
              <Col className="signup-text" xs={8}>
                <p>Already have an account?</p>
              </Col>
              <Col className="signup-link" xs={4} onClick={() => {
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
