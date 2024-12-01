<script setup lang="ts"></script>

<template>
	<div class="cell-wrapper">
		<slot></slot>
	</div>
</template>

<style scoped lang="scss">
.cell-wrapper {
	display: flex;
	flex-direction: column;
	justify-content: center;
	align-items: flex-start;

	width: fit-content;

	overflow-x: hidden;
}
</style>
