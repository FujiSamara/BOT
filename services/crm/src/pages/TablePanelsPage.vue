<script setup lang="ts">
import { computed, onMounted, useTemplateRef } from "vue";

import { useNetworkStore } from "@/store/network";
import { getTablesByAccesses } from "@/pages/panels";
import { TableService } from "@/services/table";

const contentRef = useTemplateRef("table-panel");
const tableService = new TableService(contentRef);
const networkStore = useNetworkStore();

const props = defineProps({
	activeLink: {
		type: String,
		required: true,
	},
});

const currentTable = computed(() => {
	return tableService.get(props.activeLink);
});

const loadTables = () => {
	const tables = getTablesByAccesses(networkStore.accesses);
	for (const table of tables) {
		tableService.register(
			table.name,
			table.create,
			table.withUpdatingLoop !== false,
		);
	}
};

onMounted(async () => {
	await tableService.startLoops();
});
loadTables();
</script>

<template>
	<div ref="table-panel" class="table-panel">
		<RouterView v-slot="{ Component }">
			<template v-if="Component && currentTable !== undefined">
				<Transition mode="out-in" name="fade">
					<KeepAlive>
						<Suspense timeout="300">
							<!-- main content -->
							<component :table="currentTable" class="panel" :is="Component">
							</component>

							<!-- loading state -->
							<template #fallback>
								<p>Loading</p>
								<!-- <LoadingPage></LoadingPage> -->
							</template>
						</Suspense>
					</KeepAlive>
				</Transition>
			</template>
		</RouterView>
	</div>
</template>

<style scoped lang="scss">
.table-panel {
	width: 100%;
	height: 100%;
}
</style>
