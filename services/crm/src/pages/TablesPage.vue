<script setup lang="ts">
import TableSidebar from "@/components/table/TableSidebar.vue";
</script>

<template>
	<div class="layout">
		<TableSidebar class="sidebar"></TableSidebar>
		<div class="content">
			<RouterView v-slot="{ Component }">
				<Suspense timeout="0">
					<template #default>
						<component class="table" :is="Component" v-if="Component">
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

<style scope lang="scss">
.layout {
	width: 100%;
	height: 100%;

	background-color: var(--body-background-color);

	.sidebar {
		position: fixed;
		left: 0;

		overflow-x: hidden;
		overflow-y: auto;

		width: var(--sidebar-width);
		height: 100%;
	}
}
</style>
