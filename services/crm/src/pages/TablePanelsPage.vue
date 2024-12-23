<script setup lang="ts">
import { LinkData } from "@/types";
import { computed, onMounted, Ref, ref, useTemplateRef, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import TableSidebar from "@/components/table/TableSidebar.vue";
import { getPanelsByAccesses } from "./panels";
import { useNetworkStore } from "@/store/network";
import { TableService } from "@/services/table";

const router = useRouter();
const route = useRoute();
const networkStore = useNetworkStore();
const links: Ref<LinkData[]> = ref([]);
const sidebarFolded = ref(false);
const contentRef = useTemplateRef("content");
const tableService = new TableService(contentRef);

const loadPanels = () => {
	const panels = getPanelsByAccesses(networkStore.accesses);
	const grantedLinks: LinkData[] = [...panels];

	if (grantedLinks.length === 0) {
		grantedLinks.push({
			label: "Нет таблиц",
			routeName: "table-default",
			iconURL: "/img/logout.svg",
			active: false,
		});
	}

	grantedLinks.push({
		label: "Выход",
		routeName: "logout",
		iconURL: "/img/logout.svg",
		active: false,
	});

	links.value = grantedLinks;

	// Calcs table height

	for (const panel of panels) {
		tableService.register(panel.name, panel.create);
	}
};
const linkChange = async (link: LinkData) => {
	const currentLink = links.value.find((val) => val.active);

	if (currentLink) currentLink.query = route.query;
	await router.push({ name: link.routeName, query: link.query });

	if (currentLink) currentLink.active = false;
	link.active = true;
};
const syncCurrentLink = async () => {
	let tableChoosed = false;
	for (const currentLink of links.value) {
		if (currentLink.routeName === route.name) {
			tableChoosed = true;
		}
	}

	if (!tableChoosed) {
		await linkChange(links.value[0]);
		return;
	}

	for (const currentLink of links.value) {
		currentLink.active = currentLink.routeName === route.name;
	}
};

const currentTable = computed(() => {
	const activeLink = links.value.find((link) => link.active);
	return tableService.get(activeLink?.name!);
});

watch(route, async () => {
	await syncCurrentLink();
});
onMounted(async () => {
	await tableService.startLoops();
});
onMounted(async () => {
	await syncCurrentLink();
});
loadPanels();
</script>

<template>
	<div class="layout">
		<TableSidebar
			:links="links"
			class="sidebar"
			@change="linkChange"
			v-model="sidebarFolded"
			:class="{ folded: sidebarFolded }"
		></TableSidebar>
		<div ref="content" class="content" :class="{ expanded: sidebarFolded }">
			<RouterView v-slot="{ Component }">
				<template v-if="Component && currentTable !== undefined">
					<Transition mode="out-in" name="fade">
						<KeepAlive>
							<Suspense timeout="0">
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
	</div>
</template>

<style scoped lang="scss">
@import "bootstrap/scss/functions";
@import "bootstrap/scss/variables";
@import "bootstrap/scss/mixins";

.layout {
	width: 100%;
	height: 100%;

	background-color: $body-background-color;

	.sidebar {
		position: fixed;
		left: 0;

		overflow-x: hidden;
		overflow-y: auto;

		width: $sidebar-width;
		height: 100%;

		transition:
			opacity 0.25s,
			transform 0.25s ease,
			width 0.25s;

		&.folded {
			width: $folded-sidebar-width;
		}
	}

	.content {
		padding: 32px 64px;
		padding-left: calc($sidebar-width + 64px);

		width: 100%;
		height: 100%;

		transition: padding-left 0.25s;

		&.expanded {
			padding-left: calc($folded-sidebar-width + 64px);
		}
	}

	@include media-breakpoint-down(lg) {
		.sidebar {
			opacity: 0;
			transform: translate(-100%);
		}
		.content,
		.content.expanded {
			padding-left: 64px;
		}
	}
}
</style>
