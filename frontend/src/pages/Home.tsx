import { useEffect, useRef, useState } from "react";
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
} from "antd";
import { useNavigate, useParams } from "react-router";
import {
  CalendarOutlined,
  CheckOutlined,
  CloseOutlined,
  EditOutlined,
  PlusOutlined,
  UserAddOutlined,
  UserOutlined,
} from "@ant-design/icons";
import InfiniteScroll from "react-infinite-scroll-component";
import { useDrag, useDrop } from "react-dnd";
import { useAuthToken } from "@/hooks/useAuthToken";
import { Sidebar } from "@/components/Sidebar";
import * as workspace from "@/api/workspace";
import * as identity from "@/api/identity";

const defaultWorkspaceName = "My Kanban Project";
type taskState = "Naming" | "Creating" | "Idle";

type TaskGroup = workspace.Group & {
  state: taskState;
  workspaceId: number;
};

type Task = workspace.Task & {
  taskGroupId: number;
  workspaceId: number;
  editing: boolean;
};

export type HomeProps = {
  title?: string;
};
export default function Home() {
  const navigate = useNavigate();
  const [accessToken, setAccessToken] = useAuthToken();
  const params = useParams();

  const [useTaskGroups, setTaskGroups] = useState<TaskGroup[]>([]);
  const [useTasks, setTasks] = useState<Task[]>([]);
  const [tasksCounter, setTasksCounter] = useState<
    { groupId: number; total: number }[]
  >([]);

  const title = params.workspaceName || defaultWorkspaceName;

  useEffect(() => {
    workspace
      .getWorkspaceByName(accessToken!, title)
      .then((res) => {
        setTaskGroups(
          res.groups.map<TaskGroup>((g) => ({
            state: "Idle",
            groupId: g.groupId,
            name: g.name,
            createdAt: g.createdAt,
            createdBy: g.createdBy,
            updatedAt: g.updatedAt,
            updatedBy: g.updatedBy,
            workspaceId: res.workspaceId,
          }))
        );

        setTasks(
          res.groups.flatMap((g) => {
            return g.tasks.map<Task>((t) => ({
              taskGroupId: g.groupId,
              taskId: t.taskId,
              title: t.title,
              dueDate: t.dueDate,
              assignedToUserId: t.assignedToUserId,
              createdBy: t.createdBy,
              createdAt: t.createdAt,
              updatedBy: t.updatedBy,
              updatedAt: t.updatedAt,
              description: t.description,
              editing: false,
              assignedTo: t.assignedTo,
              workspaceId: res.workspaceId,
            }));
          })
        );

        setTasksCounter(
          res.groups.map((g) => ({
            groupId: g.groupId,
            total: g.tasks.length,
          }))
        );
      })
      .catch((err) => {
        console.error("Failed to fetch workspace:", err);
      });
  }, [accessToken, title]);

  const handleLogout = async () => {
    await identity.logout();
    setAccessToken(null);
    navigate("/login");
  };

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Layout.Header className="flex justify-between items-center">
        <div className="text-white font-bold text-xl">Task Manager</div>
        <Button onClick={handleLogout}>Logout</Button>
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
                    useTasks={useTasks}
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
  onFinish?: (val: { title: string }) => void;
};

const TitleEdit = ({ value, onFinish }: TitleEditProps) => {
  return (
    <Form layout="horizontal" className="w-full" onFinish={onFinish}>
      <Form.Item noStyle className="w-full" name="title" initialValue={value}>
        <Input autoFocus />
      </Form.Item>
      <Flex
        justify="flex-end"
        align="center"
        gap={2}
        className="z-10 w-full absolute right-2"
      >
        <Form.Item>
          <Button
            htmlType="submit"
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
  assignedToUserId: number | null;
  assignedTo: string | null;
};

type TaskFormProps = {
  taskId?: React.Key;
  onFinish?: (val: TaskFormValues) => void;
  onBlur?: () => void;
};

const TaskForm = ({ onFinish, onBlur, taskId }: TaskFormProps) => {
  const [assigned, setAssigned] = useState<identity.User | null>(null);
  const formRef = useRef<HTMLDivElement>(null);
  const [form] = Form.useForm<TaskFormValues>();

  useEffect(() => {
    form.setFieldsValue({
      assignedToUserId: assigned?.accountId || null,
      assignedTo: assigned?.fullName || null,
    });
  }, [assigned, form]);

  const [isUserAssginedPopoverOpen, setIsUserAssginedPopoverOpen] =
    useState(false);

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
            open={isUserAssginedPopoverOpen}
            onOpenChange={setIsUserAssginedPopoverOpen}
            content={
              <UserAssignPopover
                assigned={assigned?.fullName || null}
                onAssigned={(e) => {
                  setAssigned(e);
                  setIsUserAssginedPopoverOpen(false);
                }}
              />
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
          <Form.Item name="assignedToUserId" noStyle hidden>
            <Input hidden />
          </Form.Item>
        </Flex>
      </Form>
    </div>
  );
};

type UserAssignPopoverProps = {
  assigned: string | null;
  onAssigned: (assignedUser: identity.User) => void;
};

const UserAssignPopover = ({
  assigned,
  onAssigned,
}: UserAssignPopoverProps) => {
  const [accessToken] = useAuthToken();
  const [query, setQuery] = useState("");

  const [users, setUsers] = useState<identity.User[]>([]);
  const [nextUsers, setNextUsers] = useState<identity.User[]>([]);

  useEffect(() => {
    identity
      .users(accessToken!, 5)
      .then((data) => {
        setUsers(data.users);

        identity
          .users(accessToken!, 5, data.users[data.users.length - 1]?.accountId)
          .then((data) => {
            setNextUsers(data.users);
          })
          .catch((error) => console.error(error));
      })
      .catch((error) => console.error(error));
  }, [accessToken]);

  const filtered = users.filter((u) =>
    u.fullName.toLowerCase().includes(query.toLowerCase())
  );

  return (
    <Space direction="vertical" className="p-2">
      <Input.Search
        placeholder="Search user"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        allowClear
      />
      <div>
        <InfiniteScroll
          dataLength={filtered.length}
          next={() => {
            setUsers((prev) => [...prev, ...nextUsers]);

            identity
              .users(
                accessToken!,
                5,
                nextUsers[nextUsers.length - 1]?.accountId
              )
              .then((data) => {
                setNextUsers(data.users);
              })
              .catch((error) => console.error(error));
          }}
          hasMore={nextUsers.length > 0}
          scrollableTarget="scrollableDiv"
          loader={<h4>Loading...</h4>}
        >
          <List
            dataSource={filtered.length > 0 ? filtered : users}
            renderItem={(item) => (
              <List.Item
                className="hover:bg-gray-100 hover:cursor-pointer mx-2 rounded-md"
                onClick={() => onAssigned(item)}
              >
                <List.Item.Meta
                  avatar={<UserOutlined />}
                  title={item.fullName}
                />
                <Button
                  disabled={assigned === item.fullName}
                  onClick={() => onAssigned(item)}
                >
                  {assigned === item.fullName ? "Assigned" : "Assign"}
                </Button>
              </List.Item>
            )}
          />
        </InfiniteScroll>
      </div>
    </Space>
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
  const [accessToken] = useAuthToken();

  const [, drop] = useDrop(
    () => ({
      accept: "task",
      drop: async (item: { id: number }) => {
        setTasks((tasks) => {
          const t = tasks.find((val) => val.taskId === item.id);

          if (t) {
            workspace
              .updateTask(accessToken!, {
                workspaceId: t.workspaceId,
                groupId: t.taskGroupId,
                taskId: t.taskId,
                toGroupId: group.groupId,
              })
              .catch((err) => console.error(err));
            t.taskGroupId = group.groupId;
          }
          return [...tasks];
        });
      },
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
              onFinish={async (val) => {
                await workspace.updateGroup(
                  accessToken!,
                  group.workspaceId,
                  group.groupId,
                  val.title
                );
                setTaskGroups((values) => {
                  const found = values.find(
                    (item) => item.groupId === group.groupId
                  );
                  if (found) {
                    found.name = val.title;
                    found.state = "Idle";
                  }
                  return [...values];
                });
              }}
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
            onFinish={async (val) => {
              const res = await workspace.createTask(accessToken!, {
                workspaceId: group.workspaceId,
                groupId: group.groupId,
                title: val.title,
                dueDate: val.date || undefined,
                assignedToUserId: val.assignedToUserId || undefined,
              });

              setTasks((values) => {
                return [
                  ...values,
                  {
                    ...res,
                    taskGroupId: group.groupId,
                    editing: false,
                    assignedTo: val.assignedTo || null,
                    workspaceId: group.workspaceId,
                  },
                ];
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
  const [accessToken] = useAuthToken();
  const dateFormater = new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
  });

  const [{ isDragging }, dragTask] = useDrag(() => ({
    type: "task",
    item: { id: task.taskId },
  }));

  const [userAssignedPopover, setUserAssignedPopover] = useState(false);

  return (
    <>
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
                onFinish={async (val) => {
                  await workspace.updateTask(accessToken!, {
                    workspaceId: task.taskGroupId,
                    groupId: task.taskGroupId,
                    taskId: task.taskId,
                    title: val.title,
                  });

                  setTask((tasks) => {
                    const t = tasks.find((v) => v.taskId === task.taskId);
                    if (t) {
                      t.title = val.title;
                      t.editing = false;
                    }

                    return [...tasks];
                  });
                }}
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
        {task.dueDate ? (
          <Tooltip
            title={`Due date on ${dateFormater.format(new Date(task.dueDate))}`}
          >
            <Flex
              justify="flex-start"
              align="center"
              gap={8}
              className="border-2 border-gray-200 rounded-md text-gray-400 w-fit"
            >
              <CalendarOutlined className="ml-2" />
              <Typography.Text className="text-gray-400 text-sm mr-2">
                {dateFormater.format(new Date(task.dueDate))}
              </Typography.Text>
            </Flex>
          </Tooltip>
        ) : null}

        <Divider size="small" />
        <Flex justify="flex-end" align="center">
          <Popover
            placement="topRight"
            trigger="click"
            open={userAssignedPopover}
            onOpenChange={setUserAssignedPopover}
            content={
              <UserAssignPopover
                assigned={task.assignedTo}
                onAssigned={async (val) => {
                  await workspace.updateTask(accessToken!, {
                    workspaceId: task.taskGroupId,
                    groupId: task.taskGroupId,
                    taskId: task.taskId,
                    assignedToUserId: val.accountId,
                  });

                  setTask((tasks) => {
                    const found = tasks.find((v) => v.taskId === task.taskId);
                    if (found) {
                      found.assignedToUserId = val.accountId;
                      found.assignedTo = val.fullName;
                    }
                    return [...tasks];
                  });
                  setUserAssignedPopover(false);
                }}
              />
            }
          >
            <Tooltip
              title={
                task.assignedTo
                  ? `Assigned to ${task.assignedTo}`
                  : "Unassigned"
              }
              placement="bottom"
            >
              <div
                className={`rounded-md bg-gray-100 hover:bg-gray-200 w-8 h-8 flex justify-center items-center text-gray-400 hover:cursor-pointer ${
                  task.assignedTo ? "border-2 border-blue-300" : null
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
