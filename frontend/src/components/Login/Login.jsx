import "./Login.css";
import Logo from "../Logo/Logo";
import {Button, Col, Form, InputGroup, Row} from "react-bootstrap";
import {EnvelopeFill, KeyFill} from "react-bootstrap-icons";

function Login(props) {
  return (
    <div className="login">
      <div className="login-container">
        {/* Make the logo occupy 10% of the height of the screen */}
        <Row className="login-logo" style={{height: "20vh"}}>
          <Logo size={"100px"}/>
        </Row>
        <Row style={{height: "10vh"}}>
          <div className="login-form-title">
            <h1>Welcome back!</h1>
          </div>
        </Row>
        <Row style={{height: "50vh"}}>
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
        </Row>
        <Row style={{height: "15vh"}}>
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
        </Row>
      </div>
    </div>
  )
}

export default Login;
