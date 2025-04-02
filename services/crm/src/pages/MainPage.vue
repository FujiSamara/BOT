<script setup lang="ts">
import { onMounted, Ref, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";

import { LinkData } from "@/types";
import { useNetworkStore } from "@/store/network";
import { getPanelsByAccesses } from "@/pages/panels";
import PageSidebar from "@/components/PageSidebar.vue";
import LoadingPage from "@/pages/LoadingPage.vue";

const router = useRouter();
const route = useRoute();
const networkStore = useNetworkStore();

const links: Ref<LinkData[]> = ref([]);
const sidebarFolded = ref(false);
const activeLink: Ref<LinkData | undefined> = ref();

const loadPanels = () => {
	const panels = getPanelsByAccesses(networkStore.accesses);
	let grantedLinks: LinkData[] = [...panels];

	if (grantedLinks.filter((val) => val.name !== "stub").length === 0) {
		grantedLinks = [
			{
				label: "Нет панелей",
				routeName: "default",
				iconURL: "/img/logout.svg",
				active: false,
			},
			...grantedLinks,
		];
	}

	grantedLinks.push({
		label: "Выход",
		routeName: "logout",
		iconURL: "/img/logout.svg",
		active: false,
	});

	links.value = grantedLinks;
};
const linkChange = async (link: LinkData) => {
	const currentLink = links.value.find((val) => val.active);

	if (currentLink) currentLink.query = route.query;
	await router.push({ name: link.routeName, query: link.query });

	if (currentLink) currentLink.active = false;
	link.active = true;
	activeLink.value = link;
};
const syncCurrentLink = async () => {
	let linkChoosed = false;
	for (const currentLink of links.value) {
		if (currentLink.routeName === route.name) {
			linkChoosed = true;
		}
	}

	if (!linkChoosed) {
		await linkChange(links.value[0]);
		return;
	}

	for (const currentLink of links.value) {
		currentLink.active = currentLink.routeName === route.name;

		if (currentLink.active) activeLink.value = currentLink;
	}
};

watch(route, async () => {
	await syncCurrentLink();
});
onMounted(async () => {
	await syncCurrentLink();
});
loadPanels();
</script>
<template>
	<div class="layout">
		<PageSidebar
			:links="links"
			class="sidebar"
			@change="linkChange"
			v-model="sidebarFolded"
			:class="{ folded: sidebarFolded }"
		></PageSidebar>
		<div class="content" :class="{ expanded: sidebarFolded }">
			<RouterView v-slot="{ Component }">
				<template v-if="Component && activeLink">
					<Transition mode="out-in" name="fade">
						<KeepAlive>
							<Suspense timeout="500">
								<!-- main content -->
								<component
									:activeLink="activeLink?.name"
									class="panel"
									:is="Component"
								>
								</component>

								<!-- loading state -->
								<template #fallback>
									<LoadingPage></LoadingPage>
								</template>
							</Suspense>
						</KeepAlive>
					</Transition>
				</template>
			</RouterView>
		</div>
	</div>
</template>
<style lang="scss" scoped>
@import "bootstrap/scss/functions";
@import "bootstrap/scss/variables";
@import "bootstrap/scss/mixins";

.layout {
	width: 100%;
	height: 100%;

	background-color: $bg-light-blue;

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

		overflow-y: auto;

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
