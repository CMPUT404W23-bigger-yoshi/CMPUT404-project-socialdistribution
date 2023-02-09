import "./Login.css";
import Logo from "../Logo/Logo";
import {Button, Col, Form, InputGroup, Row} from "react-bootstrap";
import {EnvelopeFill, KeyFill} from "react-bootstrap-icons";

function Login(props) {
  return (
    <div className="login">
      <div className="login-container">
        <Logo size={"100px"}/>
        <div className="login-form">
          <div className="login-form-title">
            <h1>Welcome back!</h1>
          </div>
          <div className="login-form-input">
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
                {/* Forgot password */}
                <Form.Text className="text-muted forgot-password">
                  <a href="/">Forgot password?</a>
                </Form.Text>

              </Form.Group>

              <Button variant="primary" type="submit">
                Login
              </Button>
            </Form>
          </div>

          <div className="login-form-signup">
            <Row xs={2}>
              <Col className="signup-text" xs={8}>
                <p>Don't have an account?</p>
              </Col>
              <Col className="signup-link" xs={4} onClick={() => {
                window.location.href = "/register"
              }}>
                <p
                >Sign up here</p>
              </Col>
            </Row>
          </div>


        </div>
      </div>
    </div>
  )
}

export default Login;
