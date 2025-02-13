<script setup lang="ts">
const props = defineProps({
	checked: {
		type: Boolean,
	},
});

const emits = defineEmits(["click"]);
</script>

<template>
	<div
		class="checkbox"
		:class="{ checked: props.checked }"
		@click="emits('click')"
	>
		<div class="icon"></div>
	</div>
</template>

<style scoped lang="scss">
.checkbox {
	@include checkbox;
}
</style>
