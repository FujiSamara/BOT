import { WorkerSchema } from "@/types";

export function formatWorker(worker: WorkerSchema): string {
	return `${worker.l_name} ${worker.f_name} ${worker.o_name}`;
}

export function formatDate(dateString: string): string {
	const date = new Date(dateString);
	return date.toLocaleDateString();
}
