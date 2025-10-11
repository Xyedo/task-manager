import { useAuth } from "@/hooks/useAuthContext";
import { PlusOutlined, RocketOutlined } from "@ant-design/icons";
import { Layout, Menu, Modal, Input, Form } from "antd";
import type { ItemType } from "antd/es/menu/interface";
import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router";
import * as workspace from "@/api/workspace";

export const Sidebar = () => {
  const navigate = useNavigate();
  const { session } = useAuth();
  const location = useLocation();
  const [useProjects, setProjects] = useState<workspace.Workspace[]>([]);

  const defaultSelectedKeys =
    decodeURIComponent(location.pathname.slice(1)) || "My Kanban Project";

  useEffect(() => {
    if (!session?.accessToken) return;
    workspace
      .listWorkspaces(session.accessToken)
      .then((res) => setProjects(res.workspaces))
      .catch((err) => {
        console.error("Failed to fetch workspaces:", err);
      });
  }, [session.accessToken]);

  const [useProjectCreating, setProjectCreating] = useState(false);
  const projectChildren = useProjects.map<ItemType>((val) => ({
    key: val.name,
    icon: null,
    label: val.name,
    onClick: () => navigate(`/${val.name}`),
  }));

  projectChildren.push({
    key: useProjects.length + 1,
    label: "New Project",
    extra: <PlusOutlined className="hover:bg-gray-200 p-2 rounded-md" />,
    onClick: () => setProjectCreating(true),
  });

  return (
    <>
      <Layout.Sider
        className="bg-white p-4 hidden md:block"
        style={{ background: "white" }}
        width={250}
      >
        <Menu
          mode="inline"
          defaultOpenKeys={["workspaces-1"]}
          defaultSelectedKeys={[defaultSelectedKeys]}
          items={[
            {
              key: "workspaces-1",
              icon: <RocketOutlined />,
              label: "Project",
              children: projectChildren,
            },
          ]}
        />
      </Layout.Sider>
      <WorkspaceCreatingModal
        open={useProjectCreating}
        setOpen={setProjectCreating}
        onCancel={() => setProjectCreating(false)}
        onOk={() => setProjectCreating(false)}
        onFinish={(v) => {
          if (!session?.accessToken) return;
          workspace
            .createWorkspace(session.accessToken, v.projectName)
            .then((res) => {
              setProjects((values) => [...values, res]);
              navigate(`/${res.name}`);
            })
            .catch((err) => {
              console.error("Failed to create workspace:", err);
            });
        }}
      />
    </>
  );
};

type FormProject = {
  projectName: string;
};
type ProjectCreateProps = {
  open: boolean;
  setOpen?: (open: boolean) => void;
  onOk?: (e: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
  onCancel?:
    | ((e: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void)
    | undefined;

  onFinish?: (v: FormProject) => void;
};

const WorkspaceCreatingModal = ({
  open,
  setOpen,
  onOk,
  onCancel,
  onFinish,
}: ProjectCreateProps) => {
  const [form] = Form.useForm<FormProject>();

  return (
    <Modal
      title="Create New Project"
      destroyOnHidden
      open={open}
      onOk={(e) => {
        form.submit();
        onOk?.(e);
      }}
      onCancel={onCancel}
    >
      <Form
        form={form}
        onFinish={onFinish}
        preserve={false}
        onKeyDown={(e) => {
          if (e.key === "Enter") {
            setOpen?.(false);
          }
        }}
      >
        <Form.Item
          name="projectName"
          label="project name"
          rules={[{ required: true }]}
        >
          <Input placeholder="Enter project name" autoFocus />
        </Form.Item>
      </Form>
    </Modal>
  );
};
