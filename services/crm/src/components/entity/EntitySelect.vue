<script setup lang="ts">
import SearchInput from "@/components/SearchInput.vue";
import { BaseEntity } from ".";
import { PropType } from "vue";

const props = defineProps({
	entity: {
		type: Object as PropType<BaseEntity<any>>,
		required: true,
	},
});
const entity = props.entity;
</script>

<template>
	<div class="entity-search">
		<SearchInput
			class="search-input"
			:value="entity.formattedField.value"
			@submit="(val: string) => (entity.formattedField.value = val)"
		></SearchInput>
	</div>
</template>

<style scoped lang="scss">
.entity-search {
	display: flex;
	flex-direction: column;

	.search-input {
		width: 248px;
	}
}
</style>
