<script setup lang="ts">
import { ref } from "vue";
</script>

<template>
	<div class="date-filter">
		<div class="mode"></div>
	</div>
</template>

<style scoped lang="scss">
.date-filter {
	@include tool;

	gap: 8px;

	.mode {
	}
}
</style>
