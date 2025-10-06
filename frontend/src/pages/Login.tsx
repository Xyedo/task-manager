import { useAuthToken } from "@/hooks/useAuthToken";
import { LockOutlined, UserOutlined } from "@ant-design/icons";
import { Button, Form, Input, Typography, Card, Space, Row, Col } from "antd";
import * as identity from "@/api/identity";
import { useNavigate } from "react-router";

export default function Login() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [, setAccessToken] = useAuthToken();
  const onFinish = async (values: { username: string; password: string }) => {
    try {
      const res = await identity.login(values.username, values.password);
      setAccessToken(res.accessToken);
      navigate("/");
    } catch (err) {
      console.error("Login failed:", err);
      form.setFields([
        {
          name: "password",
          errors: ["Invalid username or password"],
        },
      ]);
    }
  };

  return (
    <Row align="middle" justify="center" className="min-h-dvh">
      <Col xs={22} sm={18} md={12} lg={8} xl={6}>
        <Card variant="borderless">
          <Space direction="vertical" size={12} className="w-full">
            <Typography.Title level={3} className="text-center m-0">
              Sign in to Task Manager
            </Typography.Title>

            <Form
              form={form}
              id="login"
              name="login"
              layout="vertical"
              onFinish={onFinish}
            >
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

            <div className="text-center text-gray-500">
              Demo credentials: <strong>user / password</strong>
            </div>
          </Space>
        </Card>
      </Col>
    </Row>
  );
}
