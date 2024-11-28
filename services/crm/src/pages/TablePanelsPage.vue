<script setup lang="ts">
import TableSidebar from "@/components/table/TableSidebar.vue";

const links = [
	{
		label: "Статьи",
		routeName: "table-expenditures",
		iconURL: "/src/assets/icons/exit.svg",
		active: false,
	},
	{
		label: "Выход",
		routeName: "exit",
		iconURL: "/src/assets/icons/exit.svg",
		active: true,
	},
];
</script>

<template>
	<div class="layout">
		<TableSidebar :links="links" class="sidebar"></TableSidebar>
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
