import { LockOutlined, UserOutlined } from "@ant-design/icons";
import { Button, Form, Input, Typography, Card, Space, Row, Col } from "antd";
import { useEffect } from "react";
import { useNavigate } from "react-router";

const { Title } = Typography;

export default function Login() {
  const navigate = useNavigate();

  const onFinish = (values: { username: string; password: string }) => {
    console.log("login", values);
    sessionStorage.setItem("auth", "1");
    navigate("/");
  };

  useEffect(() => {
    const onEnter = (e: KeyboardEvent) => {
      if (e.key === "Enter") {
        const form = document.getElementById("login");
        if (form) {
          form.dispatchEvent(
            new Event("submit", { cancelable: true, bubbles: true })
          );
        }
      }
    };

    window.addEventListener("keydown", onEnter);
    return () => window.removeEventListener("keydown", onEnter);
  }, []);

  return (
    <Row align="middle" justify="center" className="min-h-dvh">
      <Col xs={22} sm={18} md={12} lg={8} xl={6}>
        <Card variant="borderless">
          <Space direction="vertical" size={12} className="w-full">
            <Title level={3} className="text-center m-0" >
              Sign in to Task Manager
            </Title>

            <Form id="login" name="login" layout="vertical" onFinish={onFinish}>
              <Form.Item
                name="username"
                label="Username"
                rules={[
                  { required: true, message: "Please input your username!" },
                ]}
              >
                <Input prefix={<UserOutlined />} placeholder="Username" />
              </Form.Item>

              <Form.Item
                name="password"
                label="Password"
                rules={[
                  { required: true, message: "Please input your password!" },
                ]}
              >
                <Input.Password
                  prefix={<LockOutlined />}
                  placeholder="Password"
                />
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit" block>
                  Sign In
                </Button>
              </Form.Item>
            </Form>

            <div  className="text-center text-gray-500">
              Demo credentials: <strong>user / password</strong>
            </div>
          </Space>
        </Card>
      </Col>
    </Row>
  );
}
