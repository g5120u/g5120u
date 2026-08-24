import { createWorkItem } from "./state-machine.js";

export function createMemoryStore(seed = []) {
  const records = new Map();

  for (const item of seed) {
    records.set(item.id, item);
  }

  return {
    getOrCreate(id) {
      if (!records.has(id)) {
        records.set(id, createWorkItem(id));
      }
      return records.get(id);
    },

    save(workItem) {
      records.set(workItem.id, workItem);
      return workItem;
    },

    list() {
      return [...records.values()];
    },
  };
}
