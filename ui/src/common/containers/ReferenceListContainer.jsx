import { connect } from 'react-redux';

import { fetchLiteratureReferences } from '../../actions/literature';
import ReferenceList from '../../literature/components/ReferenceList';
import { LITERATURE_REFERENCES_NS } from '../../search/constants';
import { convertSomeImmutablePropsToJS } from '../immutableToJS';

const stateToProps = (state) => ({
  loading: state.literature.get('loadingReferences'),
  references: state.literature.get('references'),
  error: state.literature.get('errorReferences'),
  total: state.literature.get('totalReferences'),
  query: state.search.getIn(['namespaces', LITERATURE_REFERENCES_NS, 'query']),
  baseQuery: state.search.getIn([
    'namespaces',
    LITERATURE_REFERENCES_NS,
    'baseQuery',
  ]),
});

const dispatchToProps = (dispatch, ownProps) => ({
  onQueryChange(query) {
    const { recordId } = ownProps;
    dispatch(fetchLiteratureReferences(recordId, query));
  },
});

export default connect(
  stateToProps,
  dispatchToProps
)(convertSomeImmutablePropsToJS(ReferenceList, ['query']));
