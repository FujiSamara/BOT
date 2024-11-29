<script setup lang="ts">
import { LinkData } from "@/types";
import { onMounted, Ref, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import TableSidebar from "@/components/table/TableSidebar.vue";
import { getPanelsByAccesses } from "./panels";
import { useNetworkStore } from "@/store/network";

const router = useRouter();
const route = useRoute();
const networkStore = useNetworkStore();

const links: Ref<LinkData[]> = ref([]);

const loadPanels = () => {
	const panels = getPanelsByAccesses(networkStore.accesses);
	const grantedLinks: LinkData[] = [...panels];

	if (grantedLinks.length === 0) {
		grantedLinks.push({
			label: "Нет таблиц",
			routeName: "table-default",
			iconURL: "/src/assets/icons/logout.svg",
			active: false,
		});
	}

	grantedLinks.push({
		label: "Выход",
		routeName: "logout",
		iconURL: "/src/assets/icons/logout.svg",
		active: false,
	});

	links.value = grantedLinks;
};

const linkChange = async (link: LinkData) => {
	await router.push({ name: link.routeName });

	for (const currentLink of links.value) {
		currentLink.active = currentLink.routeName === link.routeName;
	}
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

watch(route, async () => {
	await syncCurrentLink();
});

onMounted(async () => {
	loadPanels();
	await syncCurrentLink();
});
</script>

<template>
	<div class="layout">
		<TableSidebar
			:links="links"
			class="sidebar"
			@change="linkChange"
		></TableSidebar>
		<div class="content">
			<RouterView v-slot="{ Component }">
				<Suspense timeout="0">
					<template #default>
						<component class="panel" :is="Component" v-if="Component">
						</component>
					</template>
					<template #fallback>
						<p>Loading</p>
						<!-- <LoadingPage></LoadingPage> -->
					</template>
				</Suspense>
			</RouterView>
		</div>
	</div>
</template>

<style scoped lang="scss">
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
	}

	.content {
		padding: 32px 64px;
		padding-left: calc($sidebar-width + 64px);

		width: 100%;
		height: 100%;
	}
}
</style>
