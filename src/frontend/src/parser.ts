import { WorkerSchema } from "@/types";

export function workerToString(worker: WorkerSchema): string {
	return `${worker.l_name} ${worker.f_name} ${worker.o_name}`;
}
