import { log } from "@/shared/logging";
import assert from "assert";
import Module from "module";
import sinon from "sinon";

const PROCESS_EVENTS = [
  "uncaughtException",
  "unhandledRejection",
  "exit",
] as const;
type ProcessEvent = (typeof PROCESS_EVENTS)[number];

function snapshotProcessListeners() {
  return new Map(
    PROCESS_EVENTS.map((event) => [event, process.listeners(event as any)])
  );
}

function restoreProcessListeners(snapshot: Map<ProcessEvent, Function[]>) {
  for (const event of PROCESS_EVENTS) {
    process.removeAllListeners(event as any);
    for (const listener of snapshot.get(event) ?? []) {
      process.on(event as any, listener as any);
    }
  }
}

describe("handleProcessIssues", () => {
  let listenersBeforeTest: Map<ProcessEvent, Function[]>;

  beforeEach(() => {
    listenersBeforeTest = snapshotProcessListeners();
  });

  afterEach(() => {
    restoreProcessListeners(listenersBeforeTest);
  });

  it("does not crash when segfault-handler is unavailable", () => {
    const warn = sinon.stub(log, "warn");
    const originalLoad = Module._load;
    sinon.stub(Module, "_load").callsFake(((
      request: string,
      parent: NodeModule | null | undefined,
      isMain: boolean
    ) => {
      if (request === "segfault-handler") {
        const error = new Error("missing native module") as NodeJS.ErrnoException;
        error.code = "MODULE_NOT_FOUND";
        throw error;
      }
      return originalLoad(request, parent, isMain);
    }) as typeof Module._load);

    const modulePath = require.resolve("@/server/shared/process");
    delete require.cache[modulePath];
    const { handleProcessIssues } = require(modulePath) as typeof import("@/server/shared/process");

    assert.doesNotThrow(() => handleProcessIssues());
    assert.ok(
      warn.calledWithMatch(
        sinon.match.string,
        sinon.match.has("error", sinon.match.instanceOf(Error))
      )
    );
  });
});
