import {
  useEffect,
  useRef,
  useState,
  type ChangeEventHandler,
  type KeyboardEventHandler,
} from "react";
import {
  Button,
  Layout,
  Typography,
  Divider,
  Card,
  Row,
  Col,
  Flex,
  Input,
  Form,
  Space,
  Tooltip,
  DatePicker,
  Popover,
  List,
  Menu,
  Modal,
} from "antd";
import { useNavigate, useParams } from "react-router";
import {
  CalendarOutlined,
  CheckOutlined,
  CloseOutlined,
  EditOutlined,
  PlusOutlined,
  RocketOutlined,
  UserAddOutlined,
  UserOutlined,
} from "@ant-design/icons";
import InfiniteScroll from "react-infinite-scroll-component";
import type { ItemType } from "antd/es/menu/interface";
import { useDrag, useDrop } from "react-dnd";

const defaultProjectName = "My Kanban Project";
type taskState = "Naming" | "Creating" | "Idle";

type TaskGroup = {
  groupId: number;
  name: string;
  state: taskState;
};

type Task = {
  taskGroupId: number;
  taskId: number;
  title: string;
  date: Date | null;
  assigned_to: string | null;
  editing: boolean;
};

export type HomeProps = {
  title?: string;
};
export default function Home() {
  const params = useParams();
  const title = params.projectName ?? defaultProjectName;
  const navigate = useNavigate();

  const logout = () => {
    sessionStorage.removeItem("auth");
    navigate("/login");
  };

  const [useTaskGroups, setTaskGroups] = useState<TaskGroup[]>([
    { groupId: 1, name: "TO DO", state: "Idle" },
    { groupId: 2, name: "In Progress", state: "Idle" },
    { groupId: 3, name: "In Review", state: "Idle" },
    { groupId: 4, name: "Done", state: "Idle" },
  ]);

  const [useTasks, setTasks] = useState<Task[]>([
    {
      taskGroupId: 1,
      taskId: 1,
      title: "Task 1",
      date: new Date(),
      assigned_to: null,
      editing: false,
    },
    {
      taskGroupId: 2,
      taskId: 2,
      title: "Task 2",
      date: new Date(),
      assigned_to: null,
      editing: false,
    },
  ]);

  const [tasksCounter, setTasksCounter] = useState([
    { groupId: 1, total: 1 },
    { groupId: 2, total: 1 },
    { groupId: 3, total: 0 },
    { groupId: 4, total: 0 },
  ]);

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Layout.Header className="flex justify-between items-center">
        <div className="text-white font-bold text-xl">Task Manager</div>
        <Button onClick={logout}>Logout</Button>
      </Layout.Header>
      <Layout>
        <Sidebar />
        <Layout>
          <Layout.Content className="m-2 md:mx-8">
            <Typography.Title level={2}> {title}</Typography.Title>
            <Divider />

            <Row gutter={{ xs: 8, sm: 16, md: 24, lg: 32 }}>
              {useTaskGroups.map((group) => (
                <Col key={group.groupId} xs={24} sm={12} md={8} lg={6}>
                  <TaskGroup
                    group={group}
                    tasksCounter={tasksCounter}
                    setTasksCounter={setTasksCounter}
                    useTasks={useTasks.filter(
                      (task) => task.taskGroupId === group.groupId
                    )}
                    setTasks={setTasks}
                    setTaskGroups={setTaskGroups}
                  />
                </Col>
              ))}
            </Row>
          </Layout.Content>
        </Layout>
      </Layout>
    </Layout>
  );
}

type TitleEditProps = {
  value?: string;
  onValueChange?: ChangeEventHandler<HTMLInputElement>;
  onPressEnter?: KeyboardEventHandler<HTMLInputElement>;
};

const TitleEdit = ({ value, onValueChange, onPressEnter }: TitleEditProps) => {
  return (
    <Form layout="horizontal" className="w-full">
      <Form.Item noStyle className="w-full">
        <Input
          autoFocus
          value={value}
          onChange={onValueChange}
          onPressEnter={onPressEnter}
        />
      </Form.Item>
      <Flex
        justify="flex-end"
        align="center"
        gap={2}
        className="z-10 w-full absolute right-2"
      >
        <Form.Item>
          <Button
            type="primary"
            size="small"
            shape="round"
            icon={<CheckOutlined />}
          />
        </Form.Item>
        <Form.Item>
          <Button
            type="primary"
            size="small"
            shape="round"
            icon={<CloseOutlined />}
          />
        </Form.Item>
      </Flex>
    </Form>
  );
};

type TaskFormValues = {
  title: string;
  date: Date | null;
  assignedTo: string | null;
};
type TaskFormProps = {
  taskId?: React.Key;
  onFinish?: (val: TaskFormValues) => void;
  onBlur?: () => void;
};
const TaskForm = ({ onFinish, onBlur, taskId }: TaskFormProps) => {
  const [assigned, setAssigned] = useState<string | null>(null);
  const formRef = useRef<HTMLDivElement>(null);
  const [form] = Form.useForm<TaskFormValues>();

  useEffect(() => {
    form.setFieldsValue({ assignedTo: assigned });
  }, [assigned, form]);

  useEffect(() => {
    function handleEnterKey(e: KeyboardEvent) {
      if (e.key === "Enter") {
        {
          form.submit();
        }
      }
    }

    function handleClick(e: MouseEvent) {
      if (!formRef.current) return;
      if (!formRef.current.contains(e.target as Node)) {
        onBlur?.();
      }
    }

    function handleFocus(e: FocusEvent) {
      if (!formRef.current) return;
      if (!formRef.current.contains(e.target as Node)) {
        onBlur?.();
      }
    }

    document.addEventListener("mousedown", handleClick);
    document.addEventListener("focusin", handleFocus);
    document.addEventListener("keydown", handleEnterKey);
    return () => {
      document.removeEventListener("mousedown", handleClick);
      document.removeEventListener("focusin", handleFocus);
      document.removeEventListener("keydown", handleEnterKey);
    };
  }, [assigned, form, onBlur, onFinish]);

  return (
    <div ref={formRef}>
      <Form
        form={form}
        key={taskId}
        className="border-2 border-blue-300 rounded-md"
        onFinish={(val) => {
          console.log(val);
          onFinish?.(val);
        }}
      >
        <Form.Item name="title">
          <Input variant="borderless" autoFocus />
        </Form.Item>
        <Divider size="small" />
        <Flex justify="space-evenly" align="center">
          <div className="rounded-md hover:bg-gray-200 mx-2 mb-4">
            <Form.Item name="date" noStyle>
              <DatePicker
                format={(val) => val.format("D MMMM")}
                variant="borderless"
                needConfirm
                classNames={{
                  root: "w-fit",
                }}
                getPopupContainer={(node) => formRef.current || node}
              />
            </Form.Item>
          </div>
          <Popover
            placement="topRight"
            trigger="click"
            className="mb-4"
            content={
              <UserAssignPopover assigned={assigned} onAssigned={setAssigned} />
            }
            getPopupContainer={(node) => formRef.current || node}
          >
            <Tooltip
              title={assigned ? `Assigned to ${assigned}` : "Assign user"}
            >
              <UserAddOutlined />
            </Tooltip>
          </Popover>
          <Form.Item name="assignedTo" noStyle hidden>
            <Input hidden />
          </Form.Item>
        </Flex>
      </Form>
    </div>
  );
};

type UserAssignPopoverProps = {
  assigned: string | null;
  onAssigned: (assigned: string) => void;
};


const UserAssignPopover = ({
  assigned,
  onAssigned,
}: UserAssignPopoverProps) => {
  const [query, setQuery] = useState("");

  const users = [
    { id: 1, name: "Alice Johnson" },
    { id: 2, name: "Bob Smith" },
    { id: 3, name: "Carol Davis" },
    { id: 4, name: "Daniel White" },
  ];

  const filtered = users.filter((u) =>
    u.name.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <Space direction="vertical" className="p-2">
      <Input.Search
        placeholder="Search user"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        allowClear
      />
      <InfiniteScroll
        dataLength={filtered.length}
        next={() => {}}
        hasMore={false}
        scrollableTarget="scrollableDiv"
        loader={<h4>Loading...</h4>}
      >
        <List
          dataSource={filtered.length > 0 ? filtered : users}
          renderItem={(item) => (
            <List.Item
              className="hover:bg-gray-100 hover:cursor-pointer mx-2 rounded-md"
              onClick={() => onAssigned(item.name)}
            >
              <List.Item.Meta avatar={<UserOutlined />} title={item.name} />
              <Button
                disabled={assigned === item.name}
                onClick={() => onAssigned(item.name)}
              >
                {assigned === item.name ? "Assigned" : "Assign"}
              </Button>
            </List.Item>
          )}
        />
      </InfiniteScroll>
    </Space>
  );
};

const Sidebar = () => {
  const [useProjects, setProjects] = useState([
    { id: 1, name: defaultProjectName },
  ]);
  const [useProjectCreating, setProjectCreating] = useState(false);
  const navigate = useNavigate();
  const projectChildren = useProjects.map<ItemType>((val) => ({
    key: val.id,
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
          defaultOpenKeys={["1"]}
          defaultSelectedKeys={["1"]}
          items={[
            {
              key: "1",
              icon: <RocketOutlined />,
              label: "Project",
              children: projectChildren,
            },
          ]}
        />
      </Layout.Sider>
      <ProjectCreateModal
        open={useProjectCreating}
        onCancel={() => setProjectCreating(false)}
        onOk={() => setProjectCreating(false)}
        onFinish={(v) => {
          setProjects((projects) => {
            const newProject = {
              id: projects.length + 1,
              name: v.projectName,
            };

            return [...projects, newProject];
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
  onOk?: (e: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void;
  onCancel?:
    | ((e: React.MouseEvent<HTMLButtonElement, MouseEvent>) => void)
    | undefined;

  onFinish?: (v: FormProject) => void;
};

const ProjectCreateModal = ({
  open,
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
      <Form form={form} onFinish={onFinish} preserve={false}>
        <Form.Item name="projectName" label="project name">
          <Input placeholder="Enter project name" />
        </Form.Item>
      </Form>
    </Modal>
  );
};

type TaskGroupProps = {
  group: TaskGroup;
  tasksCounter: { groupId: number; total: number }[];
  setTasksCounter: React.Dispatch<
    React.SetStateAction<{ groupId: number; total: number }[]>
  >;
  useTasks: Task[];
  setTasks: React.Dispatch<React.SetStateAction<Task[]>>;
  setTaskGroups: React.Dispatch<React.SetStateAction<TaskGroup[]>>;
};



const TaskGroup = ({
  group,
  tasksCounter,
  setTasksCounter,
  useTasks,
  setTasks,
  setTaskGroups,
}: TaskGroupProps) => {
  const [, drop] = useDrop(
    () => ({
      accept: "task",
      drop: (item: {id: number}) =>
        setTasks((tasks) => {
          const t = tasks.find((val) => val.taskId === item.id);
          if (t) t.taskGroupId = group.groupId;
          return [...tasks];
        }),
    }),
    []
  );
  return (
    <Card
      ref={drop}
      title={
        <Flex
          gap="middle"
          align="center"
          justify="flex-start"
          className="rounded-md hover:cursor-pointer hover:bg-gray-200"
          onClick={() => {
            setTaskGroups((values) => {
              const found = values.find(
                (item) => item.groupId === group.groupId
              );
              if (found) found.state = "Naming";

              return [...values];
            });
          }}
          onBlur={() =>
            setTaskGroups((values) => {
              const found = values.find(
                (item) => item.groupId === group.groupId
              );
              if (found) found.state = "Naming";
              return [...values];
            })
          }
        >
          {group.state === "Naming" ? (
            <TitleEdit
              value={group.name}
              onValueChange={(e) => {
                setTaskGroups((values) => {
                  const found = values.find(
                    (item) => item.groupId === group.groupId
                  );
                  if (found) found.name = e.target.value;
                  return [...values];
                });
              }}
              onPressEnter={() =>
                setTaskGroups((values) => {
                  const found = values.find(
                    (item) => item.groupId === group.groupId
                  );
                  if (found) found.state = "Idle";
                  return [...values];
                })
              }
            />
          ) : (
            <>
              <Typography.Text strong>{group.name}</Typography.Text>
              <Typography.Text
                type="secondary"
                className="bg-gray-100 w-4 text-center rounded-sm"
              >
                {
                  tasksCounter.find((item) => item.groupId === group.groupId)
                    ?.total
                }
              </Typography.Text>
            </>
          )}
        </Flex>
      }
      size="small"
      className={`mb-4`}
    >
      <Space direction="vertical" size="middle" className="w-full">
        {useTasks
          .filter((task) => task.taskGroupId === group.groupId)
          .map((task) => {
            return (
              <>
                <TaskCard key={task.taskId} task={task} setTask={setTasks} />
              </>
            );
          })}
        {group.state === "Creating" ? (
          <TaskForm
            onFinish={(val) => {
              setTasks((values) => {
                const newtask = {
                  taskGroupId: group.groupId,
                  taskId: values.length + 1,
                  title: val.title,
                  date: val.date,
                  assigned_to: val.assignedTo,
                  editing: false,
                };

                return [...values, newtask];
              });

              setTaskGroups((values) => {
                const found = values.find(
                  (item) => item.groupId === group.groupId
                );
                if (found) found.state = "Idle";

                return [...values];
              });

              setTasksCounter((values) => {
                const found = values.find(
                  (item) => item.groupId === group.groupId
                );
                if (found) found.total += 1;
                return [...values];
              });
            }}
            onBlur={() => {
              setTaskGroups((values) => {
                const found = values.find(
                  (item) => item.groupId === group.groupId
                );
                if (found) found.state = "Idle";

                return [...values];
              });
            }}
          />
        ) : (
          <div className="w-full h-10 hover:cursor-pointer">
            <Form
              className="mt-2 opacity-0 hover:opacity-100"
              style={{
                opacity: group.groupId === 1 ? 1 : undefined,
              }}
              onSubmitCapture={(e) => {
                e.preventDefault();

                setTaskGroups((values) => {
                  const found = values.find(
                    (item) => item.groupId === group.groupId
                  );
                  if (found) found.state = "Creating";
                  return [...values];
                });
              }}
            >
              <Form.Item>
                <Button
                  type="default"
                  htmlType="submit"
                  block
                  icon={<PlusOutlined />}
                >
                  Create
                </Button>
              </Form.Item>
            </Form>
          </div>
        )}
      </Space>
    </Card>
  );
};

type TaskCardProps = {
  task: Task;
  setTask: React.Dispatch<React.SetStateAction<Task[]>>;
};

const TaskCard = ({ task, setTask }: TaskCardProps) => {
  const dateFormater = new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
  });

  const [{ isDragging }, dragTask] = useDrag(() => ({
    type: "task",
    item: { id: task.taskId },
  }));

  return (
    <>
      {/* <DragPreviewImage connect={preview} src={knightImage} /> */}
      <Card
        ref={dragTask}
        style={{ opacity: isDragging ? 0.5 : 1 }}
        type="inner"
        key={task.taskId}
        className="group hover:cursor-pointer hover:shadow-md hover:bg-gray-50"
        onBlur={() =>
          setTask((tasks) => {
            const t = tasks.find((val) => val.taskId === task.taskId);
            if (t) t.editing = false;

            return [...tasks];
          })
        }
        title={
          <>
            {task.editing ? (
              <TitleEdit
                value={task.title}
                onValueChange={(e) =>
                  setTask((tasks) => {
                    const t = tasks.find((val) => val.taskId === task.taskId);
                    if (t) t.title = e.target.value;

                    return [...tasks];
                  })
                }
                onPressEnter={() =>
                  setTask((tasks) => {
                    const t = tasks.find((val) => val.taskId === task.taskId);
                    if (t) t.editing = false;

                    return [...tasks];
                  })
                }
              />
            ) : (
              <Flex
                justify="flex-start"
                align="center"
                gap="small"
                className=""
              >
                <Typography.Text>{task.title}</Typography.Text>
                <div
                  className="rounded-md p-1 hover:bg-gray-200"
                  onClick={() => {
                    setTask((values) => {
                      const found = values.find(
                        (item) => item.taskId === task.taskId
                      );
                      if (found) found.editing = true;
                      return [...values];
                    });
                  }}
                  onBlur={() =>
                    setTask((values) => {
                      const found = values.find(
                        (item) => item.taskId === task.taskId
                      );
                      if (found) found.editing = false;
                      return [...values];
                    })
                  }
                >
                  <EditOutlined className="opacity-0 group-hover:opacity-100 transition" />
                </div>
              </Flex>
            )}
          </>
        }
      >
        {task.date ? (
          <Tooltip
            title={`Due date on ${dateFormater.format(new Date(task.date))}`}
          >
            <Flex
              justify="flex-start"
              align="center"
              gap={8}
              className="border-2 border-gray-200 rounded-md text-gray-400 w-fit"
            >
              <CalendarOutlined className="ml-2" />
              <Typography.Text className="text-gray-400 text-sm mr-2">
                {dateFormater.format(new Date(task.date))}
              </Typography.Text>
            </Flex>
          </Tooltip>
        ) : null}

        <Divider size="small" />
        <Flex justify="flex-end" align="center">
          <Popover
            placement="topRight"
            trigger="click"
            content={
              <UserAssignPopover
                assigned={task.assigned_to}
                onAssigned={(val) => {
                  setTask((tasks) => {
                    const found = tasks.find((v) => v.taskId === task.taskId);
                    if (found) found.assigned_to = val;
                    return [...tasks];
                  });
                }}
              />
            }
          >
            <Tooltip
              title={
                task.assigned_to
                  ? `Assigned to ${task.assigned_to}`
                  : "Unassigned"
              }
              placement="bottom"
            >
              <div
                className={`rounded-md bg-gray-100 hover:bg-gray-200 w-8 h-8 flex justify-center items-center text-gray-400 hover:cursor-pointer ${
                  task.assigned_to ? "border-2 border-blue-300" : null
                }`}
              >
                <UserOutlined />
              </div>
            </Tooltip>
          </Popover>
        </Flex>
      </Card>
    </>
  );
};
