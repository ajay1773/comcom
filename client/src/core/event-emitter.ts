import mitt, { type Emitter } from "mitt";
import { EVENT_EMITTER_ADD_WORKFLOW_JSON } from "../config";

type Events = {
  [EVENT_EMITTER_ADD_WORKFLOW_JSON]: { template: string; payload: unknown };
};

const emitter: Emitter<Events> = mitt<Events>();

export default emitter;
