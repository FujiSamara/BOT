<script setup lang="ts">
import FujiHeader from "@/components/FujiHeader.vue";
</script>

<template>
	<div class="table-sidebar">
		<FujiHeader class="header"></FujiHeader>
	</div>
</template>

<style scoped lang="scss">
.table-sidebar {
	display: flex;
	flex-direction: column;
	justify-content: flex-start;

	padding: 46px 32px 64px 32px;

	background-color: $sidebar-background-color;

	.header {
	}
}
</style>
